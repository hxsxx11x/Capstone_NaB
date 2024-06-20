from django.apps import AppConfig
import easyocr

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    reader = None

    def ready(self):
        MainConfig.reader = easyocr.Reader(['ko', 'en'], gpu=True)