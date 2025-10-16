from django import forms
from .models import Meeting, Note, Attendee, Comment


class MeetingForm(forms.ModelForm):
    """Form for creating and editing meetings"""
    visibility = forms.ChoiceField(
        choices=[
            (Meeting.VISIBILITY_TEAM, 'Team'),
            (Meeting.VISIBILITY_PUBLIC, 'Public'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Meeting
        fields = ['title', 'date', 'location', 'description', 'visibility']
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


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
