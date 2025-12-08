from django.urls import path
from . import views

urlpatterns = [
    path('redirects/', views.RedirectList.as_view(), name='redirect-list'),
    path('redirects/<path:path>/', views.RedirectDetail.as_view(), name='redirect-detail'),
]

