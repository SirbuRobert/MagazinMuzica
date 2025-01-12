from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('magazin/', include('magazin.urls')),
]

if settings.DEBUG:  # Adăugăm această condiție pentru mediul de dezvoltare
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)