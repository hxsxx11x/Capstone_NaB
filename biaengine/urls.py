from django.urls import path
from .views import *

app_name = 'biaengine'

urlpatterns = [
    path('status/', status_predict, name='status'),
    path('makemodel', make_model, name='makemodel')
]
