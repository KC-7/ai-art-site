from django import forms
from django.utils.text import slugify
from .models import Comment, Post, Profile


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)


class PostForm(forms.ModelForm):
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Post
        fields = ['post_image', 'title', 'description']

    def save(self, commit=True):
        instance = super(PostForm, self).save(commit=False)
        instance.slug = slugify(self.cleaned_data['title'])
        if commit:
            instance.save()
        return instance


class GenerateForm(forms.Form):
    prompt = forms.CharField(
        label='Enter your prompt here', max_length=1000,  # 1000 is current max limit for API
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. "An abstract painting of a sunset"'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']
