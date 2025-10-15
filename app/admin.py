from django.contrib import admin
from .models import Meeting, Note, Attendee


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'location', 'created_by', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['title', 'description', 'location']
    date_hierarchy = 'date'


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'created_by', 'created_at']
    list_filter = ['created_at', 'meeting']
    search_fields = ['content']


@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['meeting__title', 'user__username']
