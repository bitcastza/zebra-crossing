import os

from .common import *

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if os.environ.get("DJANGO_DEBUG"):
    DEBUG = True
else:
    DEBUG = False
