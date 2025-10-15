from django import forms
from .models import Meeting, Note, Attendee


class MeetingForm(forms.ModelForm):
    """Form for creating and editing meetings"""
    class Meta:
        model = Meeting
        fields = ['title', 'date', 'location', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4}
            ),
        }


class NoteForm(forms.ModelForm):
    """Form for creating and editing notes"""
    class Meta:
        model = Note
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 6}
            ),
        }


class AttendeeForm(forms.ModelForm):
    """Form for adding attendees to meetings"""
    class Meta:
        model = Attendee
        fields = ['user', 'status']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
