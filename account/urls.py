from django.urls import path
from .views import *

app_name = 'account'

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),  # /login/으로 접속하면 login_view 함수가 호출됩니다.
]