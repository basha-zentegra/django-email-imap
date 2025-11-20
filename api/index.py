import os
import sys

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_email_imap.settings")

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
