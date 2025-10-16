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


class MeetingDeleteTests(TestCase):
	def setUp(self):
		from django.contrib.auth import get_user_model
		User = get_user_model()
		self.owner = User.objects.create_user(username='owner', password='pass')
		self.other = User.objects.create_user(username='other', password='pass')

		self.meeting = Meeting.objects.create(
			title='Delete Me',
			date=timezone.now(),
			description='To be deleted',
			created_by=self.owner,
		)

		# create associated records
		self.note = Note.objects.create(meeting=self.meeting, content='Note', created_by=self.owner)
		ActionItem.objects.create(meeting=self.meeting, title='Action', description='Do it')
		Attachment.objects.create(meeting=self.meeting, name='Attach', file_url='http://example.com', uploaded_by=self.owner)

	def test_owner_sees_confirm_delete(self):
		self.client.login(username='owner', password='pass')
		resp = self.client.get(reverse('meeting_delete', args=[self.meeting.pk]))
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'Are you sure')

	def test_owner_can_delete_and_cascade(self):
		self.client.login(username='owner', password='pass')
		resp = self.client.post(reverse('meeting_delete', args=[self.meeting.pk]))
		# should redirect to meeting_list
		self.assertEqual(resp.status_code, 302)
		# meeting and related objects should be gone
		self.assertFalse(Meeting.objects.filter(pk=self.meeting.pk).exists())
		self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())
		self.assertFalse(ActionItem.objects.filter(meeting=self.meeting).exists())
		self.assertFalse(Attachment.objects.filter(meeting=self.meeting).exists())

	def test_delete_failure_rolls_back_and_shows_error(self):
		# Simulate delete failure by patching Meeting.delete to raise
		from unittest.mock import patch

		self.client.login(username='owner', password='pass')
		with patch('app.models.Meeting.delete') as mocked_delete:
			mocked_delete.side_effect = Exception('DB failure')
			resp = self.client.post(reverse('meeting_delete', args=[self.meeting.pk]))
			# Expect a 500-style response or error message (we'll treat non-302 as failure)
			self.assertNotEqual(resp.status_code, 302)
			# Nothing should have been deleted
			self.assertTrue(Meeting.objects.filter(pk=self.meeting.pk).exists())
			self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())


	class MeetingEditAuditTests(TestCase):
		def setUp(self):
			from django.contrib.auth import get_user_model
			User = get_user_model()
			self.owner = User.objects.create_user(username='owner', password='pass')
			self.meeting = Meeting.objects.create(
				title='Audit Meeting',
				date=timezone.now(),
				description='Audit',
				created_by=self.owner,
			)

		def test_edit_sets_last_edited_and_updates_timestamp(self):
			self.client.login(username='owner', password='pass')
			old_updated = self.meeting.updated_at
			resp = self.client.post(reverse('meeting_edit', args=[self.meeting.pk]), {
				'title': 'Audit Meeting Edited',
				'date': self.meeting.date.strftime('%Y-%m-%dT%H:%M'),
				'location': 'Room 1',
				'description': 'Edited',
			})
			self.assertEqual(resp.status_code, 302)
			self.meeting.refresh_from_db()
			self.assertEqual(self.meeting.last_edited_by, self.owner)
			self.assertNotEqual(self.meeting.updated_at, old_updated)
