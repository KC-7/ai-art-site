from .models import Comment, Post
from django import forms
from django.utils.text import slugify


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
