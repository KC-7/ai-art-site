from . import views
from django.urls import path


urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('upload/', views.UploadForm.as_view(), name='upload_form'),
    path('generate_art/', views.GenerateArt.as_view(), name='generate_art'),
    path('search/', views.Search.as_view(), name='search'),
    path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('like/<slug:slug>/', views.PostLike.as_view(), name='post_like'),
    path('private/<slug:slug>/', views.PostPrivate.as_view(), name='post_private'),
    path('public/<slug:slug>/', views.PostPublic.as_view(), name='post_public'),
    path('delete/<slug:slug>/', views.DeletePost.as_view(), name='delete_post'),
    path('profile/<str:username>/', views.UserProfile.as_view(), name='user_profile'),
    path('post_edit/<slug:slug>/', views.EditPost.as_view(), name='edit_post'),
]
