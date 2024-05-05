from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.management import call_command


@shared_task
def scrape_techcrunch_categories_task():
    call_command('scrape_categories_techcrunch')


@shared_task
def scrape_techcrunch_task(search_term):
    call_command('scrape_techcrunch', search_term)
