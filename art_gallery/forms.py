from django import forms
from django.utils.text import slugify
from .models import Comment, Post, Profile


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
        label='Enter your prompt here', max_length=1000,  # 1000 is current max limit for API
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. "An abstract painting of a sunset"'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ProfileForm(forms.ModelForm):
    """
    Form for editing user profile.
    """
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
