"""
This module contains all of the views for the art_gallery application.
"""

# Python Libraries
import os
from io import BytesIO
from datetime import datetime, timedelta

# Django Libraries
from django.utils import timezone
from django.utils.text import slugify
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import generic, View
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView, UpdateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db import models
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse

# Third Party Libraries
# import requests
from requests import get
from openai import api_key
from cloudinary import uploader
from PIL import Image

# Local Imports
from .utils import generate_image_from_text
from .models import Post, Profile, StaticPage
from .forms import CommentForm, PostForm, GenerateForm
from .forms import ProfileForm, EditPostForm  # Line split as too long

# Environment Variables
if os.path.isfile('env.py'):
    import env


# OpenAI API Key
api_key = os.environ['OPENAI_API_KEY']


class RegisterUser(FormView):
    """
    Creates user profile after successful registration.
    Bug Fix: This  is required to generate the art (due to the
    user limit check), without this the user profile is created
    only when the user accesses their profile which was preventing
    art generations for time new users who had not clicked on their
    profile yet. Improvement: This View could be replaced with
    Django Signals in the Models file.
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


class PostList(ListView):
    """
    Displays list of posts, paginates and allows
    sorting by most likes or most recent.
    """
    model = Post
    template_name = 'index.html'
    paginate_by = 9  # Django will restrict 9 posts to paginate_by

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        queryset = Post.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query),
            status=1
        )

        # Bug Fix - Filter out posts without a slug value
        queryset = queryset.filter(~Q(slug=''))

        sorting = self.request.GET.get('sorting', 'newest')

        if sorting == 'most_likes':
            queryset = queryset.annotate(
                likes_count=models.Count('likes')
            ).order_by('-likes_count', '-created_on')
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
            messages.success(
                request, 'Your comment has been submitted successfully')
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


class GenerateArt(FormView, LoginRequiredMixin):
    """
    Handles the art generation requests and then creates a public post.
    """
    template_name = 'generate_art.html'
    form_class = GenerateForm

    def form_valid(self, form):
        """
        Ensure form is valid before attempting to create the post.
        """
        user_profile = self.request.user.profile

        if not self.can_generate(user_profile):
            messages.error(
                self.request,
                ("You have reached your daily limit of 5 AI art generations."
                 "Please try again tomorrow.")
            )
            return self.form_invalid(form)

        prompt = form.cleaned_data['prompt']
        prompt = prompt.replace('"', '')  # replace " with empty string
        image_url = self.generate_image(prompt)

        if not image_url:
            messages.error(
                self.request,
                ("We could not generate your requested image."
                 "This may have been due to your search terms."
                 "Please read the usage policy and try again.")
            )
            return self.form_invalid(form)

        post = self.create_post(prompt, image_url)
        self.update_user_generation_counter(user_profile)

        return redirect('post_detail', slug=post.slug)

    def can_generate(self, user_profile):
        """
        Ensures the user is below their daily threshold before generating.
        """
        now = timezone.now()

        if user_profile.last_generation_timestamp:
            time_since_last_gen = now - user_profile.last_generation_timestamp
            if time_since_last_gen > timedelta(days=1):
                self.reset_generation_counter(user_profile)

        return user_profile.generation_count < 5

    def reset_generation_counter(self, user_profile):
        """
        Resets the user's generation counter and saves the profile.
        """
        user_profile.generation_count = 0
        user_profile.last_generation_timestamp = timezone.now()
        user_profile.save()

    def generate_image(self, prompt):
        """
        Generates the image using "generate_image_from_text"
        function in the utils.py file.
        """
        try:
            return generate_image_from_text(prompt)
        except ValueError:
            return None

    def create_post(self, prompt, image_url):
        """
        Creates the post using the generated image.
        """
        # response = requests.get(image_url)
        response = get(image_url)
        image_io = BytesIO(response.content)
        image = Image.open(image_io)

        output_io = BytesIO()
        image.save(output_io, format="JPEG")
        output_io.seek(0)

        post = Post()
        post.title = f"Generation for: '{prompt[:75]}...'"

        # Check if there is an existing post with same title,
        # if so add a number to the end and increment by 1
        # to ensure it is unique.
        counter = 1
        while Post.objects.filter(title=post.title).exists():
            counter += 1
            post.title = f"Generation for: '{prompt[:75]}...' ({counter})"

        post.description = ('AI-generated art based on the prompt: '
                            F'"{prompt}". \n'
                            'Created using Cre8AI.art.')
        post.creator = self.request.user
        post.status = 1  # Make the post public by default

        post.slug, public_id = self.generate_unique_slug_and_public_id(prompt)

        uploaded_image = uploader.upload(
            output_io,
            public_id=public_id,
            format="jpg",
        )

        post.post_image = uploaded_image['public_id']
        post.save()

        return post

    def generate_unique_slug_and_public_id(self, prompt):
        """
        Creates a unique slug and public ID.
        """
        shortened_prompt = prompt[:50]
        base_slug = slugify(shortened_prompt)
        slug = base_slug
        public_id = base_slug
        counter = 1

        while Post.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            public_id = f"{base_slug}-{counter}"
            counter += 1

        return slug, public_id

    def update_user_generation_counter(self, user_profile):
        """
        Updates the users daily generation counter.
        """
        now = timezone.now()
        user_profile.generation_count += 1
        user_profile.last_generation_timestamp = now
        user_profile.save()


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


class Search(PostList):
    """
    Handles user image searches.
    """
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        sorting = self.request.GET.get('sorting', 'newest')
        queryset = Post.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            status=1
        )

        if sorting == 'most_likes':
            queryset = queryset.annotate(
                likes_count=models.Count('likes')
            ).order_by('-likes_count', '-created_on')
        else:
            queryset = queryset.order_by('-created_on')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


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
