"""
WSGI config for meeting_notes project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Import env.py for local development (Code Institute pattern)
if os.path.isfile('env.py'):
    import env  # noqa

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meeting_notes.settings')

application = get_wsgi_application()
