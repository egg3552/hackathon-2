from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Meeting, Note, Attendee, ActionItem, Attachment
from django.utils import timezone


class MeetingDetailTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.user1 = User.objects.create_user('owner', password='pass')
		self.user2 = User.objects.create_user('attendee', password='pass')
		self.user3 = User.objects.create_user('other', password='pass')

		self.meeting = Meeting.objects.create(
			title='Test Meeting',
			date=timezone.now(),
			location='Virtual',
			description='A test meeting',
			created_by=self.user1
		)

		# add a note and attendee
		self.note = Note.objects.create(meeting=self.meeting, content='Note 1', created_by=self.user1)
		Attendee.objects.create(meeting=self.meeting, user=self.user2, status='accepted')

		# add action item and attachment
		ActionItem.objects.create(meeting=self.meeting, title='Do thing', description='Important', assigned_to=self.user2)
		Attachment.objects.create(meeting=self.meeting, name='Agenda', file_url='http://example.com/agenda.pdf', uploaded_by=self.user1)

	def test_owner_sees_meeting_detail_and_sections(self):
		self.client.login(username='owner', password='pass')
		resp = self.client.get(reverse('meeting_detail', args=[self.meeting.pk]))
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'Test Meeting')
		self.assertContains(resp, 'Notes')
		self.assertContains(resp, 'Attendees')
		self.assertContains(resp, 'Action Items')
		self.assertContains(resp, 'Attachments')

	def test_attendee_can_view_meeting(self):
		self.client.login(username='attendee', password='pass')
		resp = self.client.get(reverse('meeting_detail', args=[self.meeting.pk]))
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'Test Meeting')

	def test_other_user_denied(self):
		self.client.login(username='other', password='pass')
		resp = self.client.get(reverse('meeting_detail', args=[self.meeting.pk]))
		self.assertEqual(resp.status_code, 403)

class AttendeeUpdateStatusTests(TestCase):
	def setUp(self):
		from django.contrib.auth import get_user_model
		User = get_user_model()
		# Users
		self.owner = User.objects.create_user(username='owner', password='pass')
		self.attendee_user = User.objects.create_user(username='attendee', password='pass')
		self.other = User.objects.create_user(username='other', password='pass')

		# Meeting
		self.meeting = Meeting.objects.create(
			title='Auth Meeting',
			date=timezone.now(),
			description='For auth tests',
			created_by=self.owner,
		)

		# Attendee record
		self.attendee = Attendee.objects.create(
			meeting=self.meeting,
			user=self.attendee_user,
			status='invited'
		)

	def test_attendee_can_update_own_status(self):
		self.client.login(username='attendee', password='pass')
		url = reverse('attendee_update_status', args=[self.attendee.pk])
		resp = self.client.post(url, {'status': 'accepted'})
		# Redirect back to meeting detail on success
		self.assertEqual(resp.status_code, 302)
		self.attendee.refresh_from_db()
		self.assertEqual(self.attendee.status, 'accepted')

	def test_owner_can_update_attendee_status(self):
		self.client.login(username='owner', password='pass')
		url = reverse('attendee_update_status', args=[self.attendee.pk])
		resp = self.client.post(url, {'status': 'accepted'})
		self.assertEqual(resp.status_code, 302)
		self.attendee.refresh_from_db()
		self.assertEqual(self.attendee.status, 'accepted')

	def test_other_user_cannot_update_status(self):
		self.client.login(username='other', password='pass')
		url = reverse('attendee_update_status', args=[self.attendee.pk])
		resp = self.client.post(url, {'status': 'accepted'})
		# Forbidden response expected
		self.assertEqual(resp.status_code, 403)
		self.attendee.refresh_from_db()
		self.assertEqual(self.attendee.status, 'invited')
