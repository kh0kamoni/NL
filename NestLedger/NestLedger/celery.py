import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "NestLedger.settings")

app = Celery("NestLedger")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
