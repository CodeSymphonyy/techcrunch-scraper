from django.shortcuts import render
from django.http import FileResponse
from django.conf import settings
import os

# Create your views here.


def download_zip_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), as_attachment=True)
        return response


def display_download_links(request):
    # Retrieve download URLs from the session for both actions
    download_urls_by_category = request.session.pop('download_urls_by_category', [])
    download_urls_by_keyword = request.session.pop('download_urls_by_keyword', [])

    # Render the template with the download URLs for both actions
    return render(request, 'scraper/download_links.html', {
        'download_urls_by_category': download_urls_by_category,
        'download_urls_by_keyword': download_urls_by_keyword,
    })
