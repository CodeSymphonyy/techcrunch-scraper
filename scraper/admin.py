from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import (Article, Keyword, Tag, Category)
from .tasks import scrape_techcrunch_task
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ScrapeTechCrunchForm
from django.shortcuts import render, redirect
import json
import csv
import os
from django.http import HttpResponseRedirect
from django.urls import reverse, path
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.conf import settings
from datetime import datetime
import zipfile
import logging


logger = logging.getLogger(__name__)

# Register your models here


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    change_list_template = "admin/scrape_keywords_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('scrape-techcrunch/', self.admin_site.admin_view(self.scrape_techcrunch), name='scrape_techcrunch'),
        ]
        final_urls = custom_urls + urls
        return final_urls

    @method_decorator(staff_member_required)
    def scrape_techcrunch(self, request):
        if request.method == 'POST':
            logger.debug("POST data: %s", request.POST)
            if 'do_action' in request.POST:
                form = ScrapeTechCrunchForm(request.POST)
                if form.is_valid():
                    search_term = form.cleaned_data['search_term']
                    logger.info(f"About to dispatch task for term: {search_term}")
                    scrape_techcrunch_task.delay(search_term)
                    logger.info(f"Task dispatched for term: {search_term}")
                    self.message_user(request, f"Scraping task initiated for '{search_term}'")
                    return HttpResponseRedirect("../")  # Redirect back to the keyword changelist
                else:
                    logger.error("Form errors: %s", form.errors)

        else:
            form = ScrapeTechCrunchForm()

        context = self.admin_site.each_context(request)
        context['form'] = form
        context['opts'] = self.model._meta
        return render(request, "admin/scrape_techcrunch.html", context)

    def has_add_permission(self, request, obj=None):
        return False  # This will disable the 'Add keyword' button


class ArticleResource(resources.ModelResource):
    class Meta:
        model = Article


def export_articles_by_category(modeladmin, request, queryset):

    download_urls = []  # Initialize an empty list to store download URLs
    base_dir = settings.MEDIA_ROOT  # Use the media root from settings
    os.makedirs(base_dir, exist_ok=True)  # Ensure the base directory exists

    for category in Category.objects.all():
        category_articles = queryset.filter(category=category)
        if not category_articles:
            continue

        category_name = category.name
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{category_name}_{date_str}"
        zip_filename = f"{base_filename}.zip"
        zip_file_path = os.path.join(base_dir, zip_filename)

        csv_file_path = os.path.join(base_dir, f"{base_filename}.csv")
        json_file_path = os.path.join(base_dir, f"{base_filename}.json")

        # Export to CSV
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ['Title', 'Publication Date', 'Content', 'Image URL', 'Created At', 'Author', 'Category', 'Tags'])
            for article in category_articles:
                tags = Tag.objects.filter(articletag__article=article).values_list('name', flat=True)
                tags_string = "; ".join(tags)
                writer.writerow([
                    article.title,
                    article.publication_date,
                    article.content,
                    article.image_url,
                    article.created_at,
                    article.author.name,
                    article.category.name,
                    tags_string
                ])

        # Export to JSON
        with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
            data = [
                {
                    'title': article.title,
                    'publication_date': article.publication_date,
                    'content': article.content,
                    'image_url': article.image_url,
                    'created_at': article.created_at,
                    'author_name': article.author.name,
                    'category_name': article.category.name,
                    'tags': list(Tag.objects.filter(articletag__article=article).values_list('name', flat=True))
                }
                for article in category_articles
            ]
            json.dump(data, jsonfile, default=str, indent=4)

        # Zip CSV and JSON files
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            zipf.write(csv_file_path, arcname=os.path.basename(csv_file_path))
            zipf.write(json_file_path, arcname=os.path.basename(json_file_path))

        # Remove the CSV and JSON files after adding them to the ZIP
        os.remove(csv_file_path)
        os.remove(json_file_path)

        download_url = request.build_absolute_uri(f'/media/{zip_filename}')
        download_urls.append((zip_filename, download_url))

    # Save to session or pass directly to the template
    request.session['download_urls_by_category'] = download_urls
    messages.success(request, "Articles exported by category successfully. Check the next page for download links.")
    return HttpResponseRedirect(reverse('your_download_page'))


def export_articles_by_keyword(modeladmin, request, queryset):
    download_urls = []  # Initialize an empty list to store download URLs

    # Create a base directory if it doesn't exist
    base_dir = settings.MEDIA_ROOT
    os.makedirs(base_dir, exist_ok=True)

    for keyword in Keyword.objects.all():
        keyword_articles = queryset.filter(keyword=keyword)
        print(f"Keyword: {keyword.keyword}, Article Count: {keyword_articles.count()}")
        if not keyword_articles:
            continue

        search_term = keyword.keyword
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{search_term}_{date_str}"
        zip_filename = f"{base_filename}.zip"
        zip_file_path = os.path.join(base_dir, zip_filename)

        csv_file_path = os.path.join(base_dir, f"{base_filename}.csv")
        json_file_path = os.path.join(base_dir, f"{base_filename}.json")

        # Export to CSV
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ['Title', 'Publication Date', 'Content', 'Image URL', 'Created At', 'Author', 'Category', 'Tags'])
            for article in keyword_articles:
                if article.keyword:
                    print(f"Exporting Article: {article.title}, Keyword: {article.keyword.keyword},"
                          f" Category: {article.category.name}")

                    # Fetch tags for the article
                    tags = Tag.objects.filter(articletag__article=article).values_list('name', flat=True)
                    tags_string = "; ".join(tags)  # Convert to string separated by semicolons
                    writer.writerow([
                        article.title,
                        article.publication_date,
                        article.content,
                        article.image_url,
                        article.created_at,
                        article.author.name,
                        article.category.name,
                        tags_string  # Add tags string here
                    ])
                else:
                    print(f"Article: {article.title} does not have an associated keyword.")
        # Export to JSON
        with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
            data = [
                {
                    'title': article.title,
                    'publication_date': article.publication_date,
                    'content': article.content,
                    'image_url': article.image_url,
                    'created_at': article.created_at,
                    'author_name': article.author.name,
                    'category_name': article.category.name,
                    'tags': list(Tag.objects.filter(articletag__article=article).values_list('name', flat=True))
                } for article in keyword_articles if article.keyword
            ]
            json.dump(data, jsonfile, default=str, indent=4)

        # Zip CSV and JSON files
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            zipf.write(csv_file_path, arcname=os.path.basename(csv_file_path))
            zipf.write(json_file_path, arcname=os.path.basename(json_file_path))

        # Remove the CSV and JSON files after adding them to the ZIP
        os.remove(csv_file_path)
        os.remove(json_file_path)

        download_url = request.build_absolute_uri(f'/media/{zip_filename}')
        download_urls.append((zip_filename, download_url))

    # Add the download URLs to the session or pass to template context
    request.session['download_urls_by_keyword'] = download_urls
    messages.success(request, "Articles exported by keyword successfully. Check the next page for download links.")
    return HttpResponseRedirect(reverse('your_download_page'))


export_articles_by_category.short_description = "Export articles by category"

export_articles_by_keyword.short_description = "Export articles by keyword"


@admin.register(Article)
class ArticleAdmin(ImportExportModelAdmin):
    resource_class = ArticleResource
    actions = [export_articles_by_category, export_articles_by_keyword]

    def changelist_view(self, request, extra_context=None):
        # Call the superclass method to get the TemplateResponse
        response = super().changelist_view(request, extra_context)

        # Check if the response context has 'cl' key which contains the ChangeList object
        if hasattr(response, 'context_data') and 'cl' in response.context_data:
            qs = response.context_data['cl'].queryset
            print("Admin queryset count:", qs.count())

        return response
