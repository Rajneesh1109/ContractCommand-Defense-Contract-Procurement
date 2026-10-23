from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('vendors/', include('vendors.urls')),
    path('procurement/', include('procurement.urls')),
    path('contracts/', include('contracts.urls')),
    path('invoicing/', include('invoicing.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
