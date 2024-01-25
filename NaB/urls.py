from django.contrib import admin
from django.urls import include, path



urlpatterns = [
    path('', include('main.urls')),
    path('account/', include('account.urls', namespace='account')),
    path('image/', include('imageinput.urls', namespace='image')),
    path('admin/', admin.site.urls),
]