# backend/taskify_backend/taskify_auth/urls.py

from django.urls import path, include
from .views import RegisterView, AdminEmployeeCreateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('admin-create-employee/', AdminEmployeeCreateView.as_view(), name='admin_create_employee'),
]
