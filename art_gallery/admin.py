from django.contrib import admin
from .models import Post, Comment, Profile, StaticPage
from django_summernote.admin import SummernoteModelAdmin


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    """
    Admin configuration for the images posts.
    """
    list_display = ('title', 'slug', 'status', 'created_on', 'approved')
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status', 'created_on')
    summernote_fields = ('description')
    actions = ['ban_posts']

    def ban_posts(self, request, queryset):
        queryset.update(approved=False)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the comments on the posts.
    """
    list_display = ('name', 'body',  'created_on', 'approved')
    list_filter = ('approved', 'created_on')
    search_fields = ['name', 'email', 'body']
    actions = ['ban_comments']

    def ban_comments(self, request, queryset):
        queryset.update(approved=False)


admin.site.register(Profile)


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    """
    Admin configuration for the static pages, displayed in About.
    """
    list_display = ('title', 'slug', 'content', 'status')
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
