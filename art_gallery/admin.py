from django.contrib import admin
from .models import Post, Comment, Profile, StaticPage
from django_summernote.admin import SummernoteModelAdmin


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    """
    Admin configuration for the images posts.
    """
    list_display = ('title', 'creator', 'number_of_likes', 'status', 'created_on')
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status', 'created_on')
    summernote_fields = ('description')
    actions = ['make_private', 'like_posts']

    def make_private(self, request, queryset):
        queryset.update(status=0)
        self.message_user(request, "Selected posts have been set to private.")

    make_private.short_description = "Make posts private"

    def like_posts(self, request, queryset):
        for post in queryset:
            post.likes.add(request.user)
        self.message_user(request, "Selected posts have been liked.")

    like_posts.short_description = "Like selected posts"

    def number_of_likes(self, obj):
        return obj.likes.count()

    number_of_likes.short_description = "Likes"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the comments on the posts.
    """
    list_display = ('body', 'name', 'post', 'created_on')
    list_filter = ('name', 'created_on')
    search_fields = ['name', 'email', 'body']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Users Profile.
    """
    list_display = ('user', 'profile_picture', 'total_posts', 'bio', 'last_generation_timestamp', 'generation_count')
    search_fields = ('user__username', 'bio')
    actions = ['reset_profile_pictures', 'reset_generation_count']

    def reset_profile_pictures(self, request, queryset):
        default_image = 'v1682601722/defaultUser_eqbmfo.png'
        queryset.update(profile_picture=default_image)
        self.message_user(request, "Selected profile pictures have been reset to the default image.")

    reset_profile_pictures.short_description = "Reset profile pictures to default"

    def reset_generation_count(self, request, queryset):
        queryset.update(generation_count=0)
        self.message_user(request, "Selected users' daily generation count has been reset to 0.")

    reset_generation_count.short_description = "Reset daily generation count to 0"

    def total_posts(self, obj):
        return obj.user.image_posts.count()

    total_posts.short_description = "Total Posts"


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    """
    Admin configuration for the static pages, displayed in About.
    """
    list_display = ('title', 'slug', 'content', 'status')
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    actions = ['make_private']

    def make_private(self, request, queryset):
        queryset.update(status=0)
        self.message_user(request, "Selected static pages have been set to private.")

    make_private.short_description = "Make static pages private"
