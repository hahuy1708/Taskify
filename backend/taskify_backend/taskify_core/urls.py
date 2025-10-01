# backend/taskify_backend/taskify_core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("leaders/", views.list_leaders, name="list_leaders"),
    path("leaders/<int:project_id>/", views.list_leaders, name="list_project_leaders"),
    path("members/", views.list_members, name="list_members"),
    path("members/<int:team_id>/", views.list_members, name="list_team_members"),
    path("teams/", views.list_team_view, name="list_teams"),  

    path("tasks/create/", views.create_task, name="create_task"),
    path("tasks/", views.list_tasks_view, name="list_tasks"),
    path("tasks/update/<int:task_id>/", views.update_task_view, name="update_task"),
    path("tasks/delete/<int:task_id>/", views.delete_task_view, name="delete-task"), 
    path("projects/", views.list_projects_view, name="list_projects"),
    path("projects/<int:project_id>/kanban/", views.retrieve_project_view, name="retrieve_project_kanban"),
    path("projects/create/", views.create_project, name="create_project"),

    path("projects/<int:project_id>/teams",views.create_team_view,name="create_team"),
    path("projects/teams/<int:team_id>/members", views.add_members_view,name="add_members"),

    path("projects/update/<int:project_id>/", views.update_project_view, name="update_project"),
    path("projects/delete/<int:project_id>/", views.delete_project_view, name="delete-project"),
]
