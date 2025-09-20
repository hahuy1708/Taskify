# backend/taskify_backend/taskify_core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("leaders/", views.list_leaders, name="list_leaders"),
    path("leaders/<int:project_id>/", views.list_leaders, name="list_project_leaders"),
    path("members/", views.list_members, name="list_members"),
    path("members/<int:team_id>/", views.list_members, name="list_team_members"),

    path("tasks/create/", views.create_task, name="create_task"),
]
