from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from users.views import users_page

urlpatterns = [
    path('', users_page, name='users_page'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('files/', include('files.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)