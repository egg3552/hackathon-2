from django.db import models
from django.contrib.auth.models import User


class Meeting(models.Model):
    """Meeting model"""
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_meetings'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title


class Note(models.Model):
    """Note model for meeting notes"""
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    content = models.TextField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Note for {self.meeting.title}"


class Attendee(models.Model):
    """Attendee model for tracking meeting participants"""
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='attendees'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attended_meetings'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('invited', 'Invited'),
            ('accepted', 'Accepted'),
            ('declined', 'Declined'),
            ('tentative', 'Tentative'),
        ],
        default='invited'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['meeting', 'user']
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.username} - {self.meeting.title}"
