"""
This module contains all of the views for the art_gallery application.
"""

# Python Libraries
import os
import sys
from io import BytesIO
from datetime import datetime, timedelta

# Django Libraries
from django.utils import timezone
from django.utils.text import slugify
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import generic, View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db import models
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse

# Third Party Libraries
import requests
import openai
import cloudinary.uploader
from PIL import Image

# Local Imports
from .utils import generate_image_from_text
from .models import Post, Profile, StaticPage
from .forms import CommentForm, PostForm, GenerateForm, ProfileForm, EditPostForm

# Environment Variables
if os.path.isfile('env.py'):
    import env


openai.api_key = os.environ['OPENAI_API_KEY']


class RegisterUser(FormView):
    """
    Creates user profile after successful registration.
    Bug Fix: This  is required to generate the art (due to the user limit check), without this
    the user profile is created only when the user accesses their profile which was preventing
    art generations for time new users who had not clicked on their profile yet.
    Improvement: This View could be replaced with Django Signals in the Models file.
    """
    template_name = 'account/signup.html'
    form_class = UserCreationForm

    def form_valid(self, form):
        user = form.save()
        # Create user profile
        Profile.objects.create(user=user)
        # Log the user in
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        return '/'


class PostList(generic.ListView):
    """
    Displays list of posts, paginates and allows sorting by most likes or most recent.
    """
    model = Post
    template_name = 'index.html'
    paginate_by = 9  # Django will restrict 9 posts to paginate_by
    # queryset = Post.objects.filter(status=1).order_by('-created_on')

    def get_queryset(self):
        queryset = Post.objects.filter(status=1)
        sorting = self.request.GET.get('sorting', 'newest')

        if sorting == 'most_likes':
            queryset = queryset.annotate(likes_count=models.Count('likes')).order_by('-likes_count', '-created_on')
        else:
            queryset = queryset.order_by('-created_on')

        return queryset


class PostDetail(View):
    """
    Displays the image post and details. Allows and displays comments.
    """
    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by('created_on')
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": False,
                "liked": liked,
                "comment_form": CommentForm()
            },
        )

    def post(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by('created_on')
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            messages.success(request, 'Your comment has been submitted successfully')
        else:
            comment_form = CommentForm()

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": True,
                "liked": liked,
                "comment_form": CommentForm()
            },
        )


class PostLike(View):
    """
    View to like / unlike posts (only once already liked).
    """
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)

        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


class UploadForm(FormView):
    """
    Handles the form for uploading the image posts.
    """
    template_name = 'upload_form.html'
    form_class = PostForm

    def form_valid(self, form):
        post = form.save(commit=False)
        post.creator = self.request.user
        post.save()
        self.object = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post_detail', args=[self.object.slug])


@method_decorator(login_required, name='dispatch')
class GenerateArt(FormView):
    """
    This view requires user authentication and uses a GenerateForm to validate input.
    It manages the generation of the image, creation of a new Post instance, and
    limits the number of generations a user can make per day.

    Attributes:
        template_name (str): The template used to render the view.
        form_class (class): The form class used to validate the input.

    Methods:
        form_valid(form): Processes the form if it is valid.
    """
    template_name = 'generate_art.html'
    form_class = GenerateForm

    def form_valid(self, form):
        """
        Processes the form if it is valid.

        1. Checks if the user has reached the daily generation limit.
        2. Generates an AI art image based on the user's prompt.
        3. Creates a new Post instance for the generated image.
        4. Increments the user's generation count.
        5. Updates the user's last_generation_timestamp.

        Args:
            form (GenerateForm): The form instance containing the user's input.

        Returns:
            HttpResponse: Redirects to the post_detail view for the newly created post.
        """
        user = self.request.user
        user_profile = user.profile
        now = timezone.now()

        # Check if the user has made any generations in the last 24 hours
        if user_profile.last_generation_timestamp:
            time_since_last_generation = now - user_profile.last_generation_timestamp

            # Reset generation_count if it's been more than 24 hours since the last generation
            if time_since_last_generation > timedelta(days=1):
                user_profile.generation_count = 0
                user_profile.save()

        # Check if the user has reached their daily limit
        if user_profile.generation_count >= 5:
            # If the user has reached the daily limit, display an error message and return an invalid form response
            messages.error(self.request, "You have reached your daily limit of 5 AI art generations. Please try again tomorrow.")
            return self.form_invalid(form)

        # Retrieve the prompt from the cleaned form data
        prompt = form.cleaned_data['prompt']

        # Attempt to generate an image URL based on the given prompt
        try:
            image_url = generate_image_from_text(prompt)
        except ValueError:
            # If image generation fails, display an error message and return an invalid form response
            messages.error(self.request, "We could not generate your requested image. This may have been due to your search terms. Please read the usage policy for unsuitable language and try again.")
            return self.form_invalid(form)

        # Fetch the generated image from the URL and create an Image object
        response = requests.get(image_url)
        image_io = BytesIO(response.content)
        image = Image.open(image_io)

        # Save the Image object to a BytesIO buffer in JPEG format
        output_io = BytesIO()
        image.save(output_io, format="JPEG")
        output_io.seek(0)

        # Create a new Post object and set its initial attributes
        post = Post()
        post.title = f"Generation for: '{prompt}'"

        # Ensure the post title is unique by appending a counter if necessary
        base_title = f"Generation for: '{prompt}'"
        counter = 1
        post.title = base_title
        while Post.objects.filter(title=post.title).exists():
            post.title = f"{base_title} ({counter})"
            counter += 1

        # Set the post description, creator and status
        post.description = f"AI-generated art based on the prompt: {prompt}. Created using cre8ai.art."
        post.creator = self.request.user
        post.status = 1  # To make the post public by default

        # Generate a unique slug and public_id
        base_slug = slugify(post.title)
        counter = 1
        post.slug = base_slug
        public_id = base_slug
        while Post.objects.filter(slug=post.slug).exists():
            post.slug = f"{base_slug}-{counter}"
            public_id = f"{base_slug}-{counter}"
            counter += 1

        # Upload the image to Cloudinary with the unique public_id
        uploaded_image = cloudinary.uploader.upload(
            output_io,
            public_id=public_id,
            format="jpg",
        )

        # Set the post_image field to the public_id returned by Cloudinary
        post.post_image = uploaded_image['public_id']
        post.save()

        # Increment the user's generation count and update the timestamp
        user_profile.generation_count += 1
        user_profile.last_generation_timestamp = now
        user_profile.save()

        # Redirect to the post_detail view for the newly created post
        return redirect('post_detail', slug=post.slug)


class PostPrivate(View):
    """
    Handles making and viewing private posts.
    """
    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=0, creator=request.user)
        post = get_object_or_404(queryset, slug=slug)

        return render(
            request,
            "post_private_detail.html",
            {
                "post": post
            },
        )

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug, creator=request.user)
        post.status = 0
        post.save()
        messages.warning(request, 'Your post has been made private.')
        return redirect('post_private', slug=post.slug)


class PostPublic(View):
    """
    Allows the user to make private posts public again.
    """
    def post(self, request, slug):
        # print(f"PostPublic - slug: {slug}")  # Debugging
        post = get_object_or_404(Post, slug=slug, creator=request.user)
        post.status = 1
        post.save()
        messages.success(request, 'Your post has been made public.')
        return redirect('post_detail', slug=post.slug)


class DeletePost(View):
    """
    Handles the deletion of posts.
    """
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug, creator=request.user)
        post.delete()
        messages.success(request, 'Your post has been deleted.')
        return redirect('user_profile', username=request.user.username)


class UserProfile(View):
    """
    Displays user profile and handels user editing of Bio and Profile Picture.
    """
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        profile = Profile.objects.get_or_create(user=user)[0]
        posts = Post.objects.filter(creator=user).order_by('-created_on')
        form = ProfileForm(instance=profile)

        context = {
            'form': form,
            'profile': profile,
            'posts': posts,
        }
        return render(request, 'user_profile.html', context)

    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        profile = Profile.objects.get_or_create(user=user)[0]
        posts = Post.objects.filter(creator=user).order_by('-created_on')

        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('user_profile', username=username)
        else:
            context = {
                'form': form,
                'profile': profile,
                'posts': posts,
            }
            return render(request, 'user_profile.html', context)


class Search(View):
    """
    Handles user images searches.
    """
    def get(self, request):
        query = request.GET.get('q', '')
        posts = Post.objects.filter(Q(title__icontains=query) | Q(description__icontains=query), status=1).order_by('-created_on')
        if posts:
            return render(request, 'search_results.html', {'posts': posts, 'query': query})
        else:
            message = "There are no matches for your search result. Sounds original, why not generate a new creation?"
            # Bug Fix: Empty 'posts' lists variable added to display 'query' when no results are available, without it it will returns empty parenthesis.
            return render(request, 'search_results.html', {'posts': [], 'message': message, 'query': query})


class EditPost(UpdateView):
    """
    Handles editing post details.
    """
    model = Post
    form_class = EditPostForm
    template_name = 'post_edit.html'

    def get_object(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Post, slug=slug, creator=self.request.user)

    def get_success_url(self):
        return reverse('post_detail', args=[self.object.slug])


class StaticPageView(TemplateView):
    """
    Handles the static pages. These can be uploaded and updated by site admins.
    """
    template_name = 'static_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = get_object_or_404(StaticPage, slug=self.kwargs['slug'])
        context['page'] = page
        return context


class AboutView(TemplateView):
    """
    Handles the about page and displays all of the admins static pages.
    """
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['public_static_pages'] = StaticPage.objects.filter(status=1)
        return context
