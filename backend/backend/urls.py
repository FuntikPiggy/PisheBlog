from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from api.views import short_link_decode

urlpatterns = [
    path('s/<str:shorturl>/', short_link_decode, name='short-link'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
