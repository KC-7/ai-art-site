from . import views
from django.urls import path


urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('upload/', views.UploadForm.as_view(), name='upload_form'),
    path('generate_art/', views.GenerateArt.as_view(), name='generate_art'),
    path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('like/<slug:slug>/', views.PostLike.as_view(), name='post_like'),
]
