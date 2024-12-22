from config.config import settings
from config.celery.connection import app as celery_app


__all__ = ('settings',
           'celery_app',
           )
