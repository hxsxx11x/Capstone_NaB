from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

urlpatterns = [
    path('', include('main.urls')),
    path('account/', include('account.urls', namespace='account')),
    path('admin/', admin.site.urls),
    path('image/', include('imageinput.urls', namespace='image')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
