import os
from pathlib import Path

# Terraform
TF_CONF_PATH = f'{Path(__file__).parents[2]}/configurations'
TF_CONFIGURATIONS = [ p.stem for p in Path(TF_CONF_PATH).iterdir() if p.is_dir() ]

# Celery
BROKER_URL = os.getenv('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
CELERY_TRACK_STARTED = True

# Celery once
ONCE = {
  'backend': 'celery_once.backends.Redis',
  'settings': {
    'url': BROKER_URL,
    'default_timeout': 60
  }
}
