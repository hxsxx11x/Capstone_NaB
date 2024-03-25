from django.urls import path
from .views import *

app_name = 'significants'

urlpatterns = [
    path('significants', significants, name='significants'),
]