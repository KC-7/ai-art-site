from django import forms
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from .models import Comment, Post, Profile


def validate_file_size(value):
    limit = 5 * 1024 * 1024  # 5 MB
    if value.size > limit:
        raise ValidationError('File size must not exceed 5 MB.')


class CommentForm(forms.ModelForm):
    """
    Form for adding comments to posts.
    """
    class Meta:
        model = Comment
        fields = ('body',)


class PostForm(forms.ModelForm):
    """
    Form for creating image posts.
    """
    # Validate image is below 5mb
    post_image = forms.ImageField(
        validators=[validate_file_size], required=False)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Post
        fields = ['post_image', 'title', 'description']

    def save(self, commit=True):
        """
        Save the post with slug based off of title.
        """
        instance = super(PostForm, self).save(commit=False)
        instance.slug = slugify(self.cleaned_data['title'])
        if commit:
            instance.save()
        return instance


class GenerateForm(forms.Form):
    """
    Form for text to image art generations.
    """
    prompt = forms.CharField(
        label='Enter your prompt here', max_length=1000,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. "Paint a futuristic city with flying cars"'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ProfileForm(forms.ModelForm):
    """
    Form for editing user profile.
    """
    profile_picture = forms.ImageField(
        validators=[validate_file_size],
        required=False)  # Validates image is below 5mb

    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']


class EditPostForm(forms.ModelForm):
    """
    Form for editing posted images description.
    """
    class Meta:
        model = Post
        fields = ['description']
