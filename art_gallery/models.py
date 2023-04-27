from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

# Posted Image Status:
STATUS = ((0, "Private"), (1, "Public"))


class Post(models.Model):
    """
    A model for the image posts.
    """
    post_image = CloudinaryField('image', blank=False, null=False)
    title = models.CharField(max_length=1000, unique=True, blank=False, null=False)
    slug = models.SlugField(max_length=1000, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="image_posts")
    updated_on = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=False, null=False)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=1)  # This makes upload public by default
    likes = models.ManyToManyField(User, related_name='image_likes', blank=True)
    approved = models.BooleanField(default=True)

    # Default ordering for image posts
    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    # Counts image likes
    def number_of_likes(self):
        return self.likes.count()


class Comment(models.Model):
    """
    A model for the comments on the image posts.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)  # Comments are visible by default

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return f"Comment {self.body} by {self.name}"


class Profile (models.Model):
    """
    A model for the user profiles.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, default='Cre8AI.art User')
    profile_picture = CloudinaryField('profile_pictures', default='v1682601722/defaultUser_eqbmfo.png')

    last_generation_timestamp = models.DateTimeField(null=True, blank=True)
    generation_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class StaticPage(models.Model):
    """
    A model for the admins static pages.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    status = models.IntegerField(choices=STATUS, default=0)  # This makes it private by default

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
