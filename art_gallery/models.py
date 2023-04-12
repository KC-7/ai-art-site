from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

STATUS = ((0, "Private"), (1, "Public"))


class Post(models.Model):
    title = models.CharField(max_length=250, unique=True, blank=False, null=False)
    slug = models.SlugField(max_length=250, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="image_posts")
    updated_on = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=False, null=False)
    post_image = CloudinaryField('image', blank=False, null=False)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=1)  # This makes user uploads public by default
    likes = models.ManyToManyField(User, related_name='image_likes', blank=True)
    approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def number_of_likes(self):
        return self.likes.count()


class Comment(models.Model):

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
