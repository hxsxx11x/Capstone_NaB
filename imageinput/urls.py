from django.urls import path
from .views import *

app_name = 'image'

urlpatterns = [
    path('upload/', fileupload, name='upload'),
    path('confirm/', confirm, name='confirm'),
]
