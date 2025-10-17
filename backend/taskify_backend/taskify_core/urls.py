# backend/taskify_backend/taskify_core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ===== User scope =====
    path("users/leaders/", views.list_leaders, name="list_system_leaders"),   # leaders toàn hệ thống
    path("users/members/", views.list_members, name="list_system_members"),   # members toàn hệ thống
    path("users/<int:user_id>/lock/", views.lock_user_view, name="lock_user"),  # khóa user (soft lock)

    # ===== Task =====
    path("tasks/create/", views.create_task, name="create_task"),
    path("tasks/", views.list_tasks_view, name="list_tasks"),
    path("tasks/update/<int:task_id>/", views.update_task_view, name="update_task"),
    path("tasks/delete/<int:task_id>/", views.delete_task_view, name="delete-task"), 


    # ===== Project =====
    path("projects/", views.list_projects_view, name="list_projects"),
    path("projects/<int:project_id>/leaders", views.list_leaders, name="list_project_leaders"),
    path("projects/<int:project_id>/kanban/", views.retrieve_project_view, name="retrieve_project_kanban"),
    path("projects/create/", views.create_project, name="create_project"),
    path("projects/update/<int:project_id>/", views.update_project_view, name="update_project"),
    path("projects/delete/<int:project_id>/", views.delete_project_view, name="delete-project"),

    # ===== Team =====
    path("projects/<int:project_id>/teams",views.create_team_view,name="create_team"),
    path("teams/<int:team_id>/members/", views.list_members, name="list_team_members"),
    path("teams/", views.list_team_view, name="list_teams"),
    path("teams/<int:team_id>/members/add/", views.add_members_view,name="add_members"),

    # ===== Comment =====
    path("tasks/<int:task_id>/comments/", views.list_comment_view, name="list_comments"),
    path("tasks/<int:task_id>/comments/create/", views.create_comment_view, name="create_comment"),
    path("comments/<int:comment_id>/update/", views.update_comment_view, name="update_comment"),
    path("comments/<int:comment_id>/delete/", views.delete_comment_view, name="delete_comment"),

    # ===== Checklist =====
    path("tasks/<int:task_id>/checklist/", views.list_checklist_items_view, name="list_checklist_items"),
    path("tasks/<int:task_id>/checklist/create/", views.create_checklist_item_view, name="create_checklist_item"),
    path("checklist/<int:item_id>/update/", views.update_checklist_item_view, name="update_checklist_item"),
    path("checklist/<int:item_id>/delete/", views.delete_checklist_item_view, name="delete_checklist_item"),

    # ===== Stats =====
    path('stats/dashboard/', views.admin_dashboard_stats, name='dashboard-stats'),
]
