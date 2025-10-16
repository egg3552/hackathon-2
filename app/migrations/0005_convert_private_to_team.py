"""Data migration to convert existing 'private' visibility to 'team'.

This keeps existing meetings visible while simplifying the UI to two options.
"""
from django.db import migrations


def convert_private_to_team(apps, schema_editor):
    Meeting = apps.get_model('app', 'Meeting')
    Meeting.objects.filter(visibility='private').update(visibility='team')


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_meeting_public_token_meeting_visibility'),
    ]

    operations = [
        migrations.RunPython(convert_private_to_team, reverse_code=migrations.RunPython.noop),
    ]
