import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sbshow.settings")

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
