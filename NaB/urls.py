from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


urlpatterns = [
    path('', lambda request:redirect('account/', permanent=False)),  # 루트 URL을 '/account/'로 리디렉션
    path('account/', include('account.urls', namespace='account')),
    path('admin/', admin.site.urls),
    path('image/', include('imageinput.urls', namespace='image')),
    path('biaengine/', include('biaengine.urls', namespace='biaengine')),
    path('significants/', include('significants.urls', namespace='significants'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
