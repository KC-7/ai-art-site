# Python Libraries
import os
import sys
from io import BytesIO

# Django Libraries
from django.utils.text import slugify
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import generic, View
from django.views.generic.edit import FormView, UpdateView
from django.contrib import messages
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse

# Third Party Libraries
import requests
import openai
import cloudinary.uploader
from PIL import Image

# Local Imports
from .utils import generate_image_from_text
from .models import Post, Profile
from .forms import CommentForm, PostForm, GenerateForm, ProfileForm, EditPostForm

# Environment Variables
if os.path.isfile('env.py'):
    import env


openai.api_key = os.environ['OPENAI_API_KEY']


class PostList(generic.ListView):
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

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)

        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


class UploadForm(FormView):
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


class GenerateArt(FormView):
    template_name = 'generate_art.html'
    form_class = GenerateForm

    def form_valid(self, form):
        prompt = form.cleaned_data['prompt']
        try:
            image_url = generate_image_from_text(prompt)
        except ValueError:
            messages.error(self.request, "We could not generate your requested image. This may have been due to your search terms. Please read the usage policy for unsuitable language and try again.")
            return self.form_invalid(form)

        response = requests.get(image_url)
        image_io = BytesIO(response.content)
        image = Image.open(image_io)

        output_io = BytesIO()
        image.save(output_io, format="JPEG")
        output_io.seek(0)

        # uploaded_image = cloudinary.uploader.upload(
        #     output_io,
        #     public_id=f"{slugify(prompt)}",
        #     format="jpg",
        # )

        post = Post()
        post.title = f"Generation for: '{prompt}'"
        # post.description = f"AI-generated art based on the prompt: {prompt}. Created using cre8ai.art."
        # post.post_image = uploaded_image['public_id']  # Sets the post_image field to the public_id returned by Cloudinary
        # post.creator = self.request.user
        # post.status = 1  # To make the post public by default
        # post.slug = slugify(post.title)
        # post.save()
        # return redirect('post_detail', slug=post.slug)

        # Generate a unique title
        base_title = f"Generation for: '{prompt}'"
        counter = 1
        post.title = base_title
        while Post.objects.filter(title=post.title).exists():
            post.title = f"{base_title} ({counter})"
            counter += 1

        post.description = f"AI-generated art based on the prompt: {prompt}. Created using cre8ai.art."
        # post.post_image = uploaded_image['public_id']  # Sets the post_image field to the public_id returned by Cloudinary
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

        # Upload the image with the unique public_id
        uploaded_image = cloudinary.uploader.upload(
            output_io,
            public_id=public_id,
            format="jpg",
        )

        # Sets the post_image field to the public_id returned by Cloudinary
        post.post_image = uploaded_image['public_id'] 

        post.save()
        return redirect('post_detail', slug=post.slug)


class PostPrivate(View):

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
    def post(self, request, slug):
        print(f"PostPublic - slug: {slug}")  # Debugging
        post = get_object_or_404(Post, slug=slug, creator=request.user)
        post.status = 1
        post.save()
        messages.success(request, 'Your post has been made public.')
        return redirect('post_detail', slug=post.slug)


class DeletePost(View):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug, creator=request.user)
        post.delete()
        messages.success(request, 'Your post has been deleted.')
        return redirect('home')


class UserProfile(View):
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
    model = Post
    form_class = EditPostForm
    template_name = 'post_edit.html'

    def get_object(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Post, slug=slug, creator=self.request.user)

    def get_success_url(self):
        return reverse('post_detail', args=[self.object.slug])


# class TermsOfUse(View):
#     def get(self, request):
#         return render(request, 'terms.html')
