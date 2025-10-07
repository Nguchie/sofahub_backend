from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.BlogPostList.as_view(), name='blog-post-list'),
    path('posts/<slug:slug>/', views.BlogPostDetail.as_view(), name='blog-post-detail'),
    path('tags/', views.BlogTagList.as_view(), name='blog-tag-list'),
]
