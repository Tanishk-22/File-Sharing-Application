from django.urls import path
from . import views
from .views import file_share
from .views import file_delete

urlpatterns = [
    path('upload/', views.file_upload, name='file_upload'),
    path('download/<int:file_id>/', views.file_download, name='file_download'),
    path('share/<int:file_id>/', file_share, name='file_share'),
    path('files/delete/<int:file_id>/', file_delete, name='file_delete'),
]