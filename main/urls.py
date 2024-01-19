from django.urls import path, include
from .views import signup_view, logout_view, home_view
from account.views import signup

urlpatterns = [
    path('', home_view, name='home'),  # 홈페이지 URL
    path('logout/', logout_view, name='logout'),  # /logout/으로 접속하면 logout_view 함수가 호출됩니다.
]