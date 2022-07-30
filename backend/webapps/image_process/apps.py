from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

class ImageProcessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webapps.image_process'

    # def ready(self):
    #     autodiscover_modules('predictor.py')