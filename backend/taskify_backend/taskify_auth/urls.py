# backend/taskify_backend/taskify_auth/urls.py

from django.urls import path, include
from .views import RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
]
