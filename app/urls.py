from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='login.html'),
        name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('meetings/', views.meeting_list, name='meeting_list'),
    path('meetings/create/', views.meeting_create, name='meeting_create'),
    path('meetings/<int:pk>/', views.meeting_detail, name='meeting_detail'),
    path(
        'meetings/<int:pk>/edit/',
        views.meeting_edit,
        name='meeting_edit'
    ),
    path(
        'meetings/<int:pk>/delete/',
        views.meeting_delete,
        name='meeting_delete'
    ),
    path(
        'meetings/<int:meeting_id>/notes/create/',
        views.note_create,
        name='note_create'
    ),
    path('notes/<int:pk>/edit/', views.note_edit, name='note_edit'),
    path('notes/<int:pk>/delete/', views.note_delete, name='note_delete'),
    path('notes/<int:note_id>/comments/add/', views.comment_create, name='comment_create'),
    path('comments/<int:pk>/edit/', views.comment_edit, name='comment_edit'),
    path('comments/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path(
        'meetings/<int:meeting_id>/attendees/add/',
        views.attendee_add,
        name='attendee_add'
    ),
    path(
        'attendees/<int:pk>/remove/',
        views.attendee_remove,
        name='attendee_remove'
    ),
    path(
        'attendees/<int:pk>/update-status/',
        views.attendee_update_status,
        name='attendee_update_status'
    ),
]
