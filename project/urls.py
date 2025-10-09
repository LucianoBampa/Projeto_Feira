from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from feirantes import views


urlpatterns = [
    path('', views.mapa_feiras, name='home'),
    path('admin/', admin.site.urls),
    # path('auth/', include('django.contrib.auth.urls')),
    path('feirantes/', include(
        ('feirantes.urls', 'feirantes'),
        namespace='feirantes')
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
