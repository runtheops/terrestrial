from __future__ import absolute_import

from celery import Celery


app = Celery('terrestrial')
app.config_from_object('terrestrial.config.celery')
