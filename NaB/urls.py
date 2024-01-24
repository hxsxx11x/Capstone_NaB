from django.contrib import admin
from django.urls import include, path



urlpatterns = [
    path('', include('main.urls')),
    path('account/', include('account.urls', namespace='account')),
    path('admin/', admin.site.urls),
]