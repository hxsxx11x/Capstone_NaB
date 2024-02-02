from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *
from imageinput.views import fileupload
app_name = 'account'

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),
    path('delete/', delete_view, name='delete'),
    path('upload/', fileupload, name='upload'),
]