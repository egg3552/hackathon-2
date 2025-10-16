from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Meeting, Note, Attendee
from .forms import MeetingForm, NoteForm, AttendeeForm


def index(request):
    """Home page"""
    return render(request, 'index.html')


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request,
                f'Account created for {username}! You can now log in.'
            )
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def dashboard(request):
    """User dashboard"""
    meetings = Meeting.objects.filter(created_by=request.user)
    attended_meetings = Meeting.objects.filter(attendees__user=request.user)
    return render(request, 'dashboard.html', {
        'meetings': meetings,
        'attended_meetings': attended_meetings
    })


@login_required
def meeting_list(request):
    """List all meetings"""
    meetings = Meeting.objects.all()
    return render(request, 'meeting_list.html', {'meetings': meetings})


@login_required
def meeting_create(request):
    """Create a new meeting"""
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.created_by = request.user
            meeting.save()
            messages.success(request, 'Meeting created successfully!')
            return redirect('meeting_detail', pk=meeting.pk)
    else:
        form = MeetingForm()
    return render(
        request,
        'meeting_form.html',
        {'form': form, 'title': 'Create Meeting'}
    )


@login_required
def meeting_detail(request, pk):
    """View meeting details"""
    meeting = get_object_or_404(Meeting, pk=pk)

    # Permission: allow access if user is the creator or an attendee
    is_creator = meeting.created_by == request.user
    is_attendee = meeting.attendees.filter(user=request.user).exists()
    if not (is_creator or is_attendee):
        return render(request, 'access_denied.html', status=403)

    notes = meeting.notes.all()
    attendees = meeting.attendees.all()
    action_items = meeting.action_items.all()
    attachments = meeting.attachments.all()
    return render(request, 'meeting_detail.html', {
        'meeting': meeting,
        'notes': notes,
        'attendees': attendees,
        'action_items': action_items,
        'attachments': attachments,
    })


@login_required
def meeting_edit(request, pk):
    """Edit a meeting"""
    meeting = get_object_or_404(Meeting, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            messages.success(request, 'Meeting updated successfully!')
            return redirect('meeting_detail', pk=meeting.pk)
    else:
        form = MeetingForm(instance=meeting)
    return render(
        request,
        'meeting_form.html',
        {'form': form, 'title': 'Edit Meeting'}
    )


@login_required
def meeting_delete(request, pk):
    """Delete a meeting"""
    meeting = get_object_or_404(Meeting, pk=pk, created_by=request.user)
    if request.method == 'POST':
        meeting.delete()
        messages.success(request, 'Meeting deleted successfully!')
        return redirect('meeting_list')
    return render(
        request,
        'meeting_confirm_delete.html',
        {'meeting': meeting}
    )


@login_required
def note_create(request, meeting_id):
    """Create a note for a meeting"""
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.meeting = meeting
            note.created_by = request.user
            note.save()
            messages.success(request, 'Note added successfully!')
            return redirect('meeting_detail', pk=meeting_id)
    else:
        form = NoteForm()
    return render(
        request,
        'note_form.html',
        {'form': form, 'meeting': meeting}
    )


@login_required
def note_edit(request, pk):
    """Edit a note"""
    note = get_object_or_404(Note, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Note updated successfully!')
            return redirect('meeting_detail', pk=note.meeting.pk)
    else:
        form = NoteForm(instance=note)
    return render(
        request,
        'note_form.html',
        {'form': form, 'meeting': note.meeting}
    )


@login_required
def note_delete(request, pk):
    """Delete a note"""
    note = get_object_or_404(Note, pk=pk, created_by=request.user)
    meeting_id = note.meeting.pk
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted successfully!')
        return redirect('meeting_detail', pk=meeting_id)
    return render(
        request,
        'note_confirm_delete.html',
        {'note': note}
    )


@login_required
def attendee_add(request, meeting_id):
    """Add an attendee to a meeting"""
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    if request.method == 'POST':
        form = AttendeeForm(request.POST)
        if form.is_valid():
            attendee = form.save(commit=False)
            attendee.meeting = meeting
            attendee.save()
            messages.success(request, 'Attendee added successfully!')
            return redirect('meeting_detail', pk=meeting_id)
    else:
        form = AttendeeForm()
    return render(
        request,
        'attendee_form.html',
        {'form': form, 'meeting': meeting}
    )


@login_required
def attendee_remove(request, pk):
    """Remove an attendee from a meeting"""
    attendee = get_object_or_404(Attendee, pk=pk)
    meeting_id = attendee.meeting.pk
    if request.method == 'POST':
        attendee.delete()
        messages.success(request, 'Attendee removed successfully!')
        return redirect('meeting_detail', pk=meeting_id)
    return render(
        request,
        'attendee_confirm_delete.html',
        {'attendee': attendee}
    )


@login_required
def attendee_update_status(request, pk):
    """Update attendee status"""
    attendee = get_object_or_404(Attendee, pk=pk)
    if request.method == 'POST':
        # Authorization: only the attendee themself, the meeting creator, or staff may update
        user = request.user
        meeting = attendee.meeting
        if not (user == attendee.user or user == meeting.created_by or user.is_staff):
            # Forbidden
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('You do not have permission to update this attendee status')

        status = request.POST.get('status')
        if status in ['invited', 'accepted', 'declined', 'tentative']:
            attendee.status = status
            attendee.save()
            messages.success(request, 'Status updated successfully!')
        return redirect('meeting_detail', pk=attendee.meeting.pk)
    return render(
        request,
        'attendee_status_form.html',
        {'attendee': attendee}
    )
