from django.urls import path
from .views import *

app_name = 'image_upload'

urlpatterns = [
    path('upload/', image_upload, name='upload'),
]
