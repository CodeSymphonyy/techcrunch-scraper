from django.urls import path
from .views import download_zip_file, display_download_links

urlpatterns = [
    path('download/<str:filename>/', download_zip_file, name='download_zip'),
    path('download-page/', display_download_links, name='your_download_page'),
]
