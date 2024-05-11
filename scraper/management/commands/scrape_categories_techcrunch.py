from django.core.management.base import BaseCommand
from scraper.models import Category, Author, Article, Tag, ArticleTag, Keyword, KeywordSearchResult, \
    KeywordSearchResultItem
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import pytz


class Command(BaseCommand):
    help = 'Scrapes articles from TechCrunch and stores them in the database'

    def handle(self, *args, **kwargs):
        base_urls = [
            'https://techcrunch.com/wp-json/tc/v1/magazine?page={'
            '}&_embed=true&_envelope=true&categories=577047203&cachePrevention=0',
            # AI
            'https://techcrunch.com/wp-json/tc/v1/magazine?page={'
            '}&_embed=true&_envelope=true&categories=577051039&cachePrevention=0',
            # APPs
            'https://techcrunch.com/wp-json/tc/v1/magazine?page={'
            '}&_embed=true&_envelope=true&categories=577030454&cachePrevention=0',
            # Biotech & Health
        ]
        all_links = []
        for base_url in base_urls:
            page = 1
            while page <= 1:
                url = base_url.format(page)
                response = requests.get(url)
                data = response.json()
                links = [item['link'] for item in data['body'] if 'link' in item]

                if not links:
                    break
                print(links)
                all_links.extend(links)
                page += 1

        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode.
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")  # Disable extensions
        chrome_options.add_argument("--disable-popup-blocking")  # Disable pop-ups
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--incognito")  # Use Chrome in Incognito mode
        chrome_options.add_argument("--single-process")  # Run Chrome in single-process mode
        chrome_options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage
        chrome_options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging
        chrome_options.add_argument("--log-level=3")  # Minimize logging
        # chrome_options.add_argument("--disable-software-rasterizer")  # Disable software rasterizer
        # chrome_options.add_argument("--disable-background-networking")  # Disable background networking
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")  # Disable Viz Display Compositor
        caps = DesiredCapabilities.CHROME
        # caps["pageLoadStrategy"] = "none"  # Do not wait for the full page to load
        caps["pageLoadStrategy"] = "eager"

        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            for url in all_links:
                response = requests.get(url)
                print(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                title_element = soup.select_one('h1.wp-block-post-title')
                if title_element:
                    title = title_element.text.strip()
                else:
                    title = "Title not found"
                publication_date_element = soup.select_one("div.wp-block-post-date > time")
                publication_date = publication_date_element['datetime'] if publication_date_element else None
                # print(f"Publication date: {publication_date}")

                if publication_date:
                    try:
                        dt = datetime.fromisoformat(publication_date)
                        localized_dt = dt if dt.tzinfo else dt.replace(tzinfo=pytz.UTC)
                    except ValueError as e:
                        print(f"Error parsing date {publication_date}: {e}")
                        localized_dt = None
                else:
                    localized_dt = None
                try:
                    article_content_elements = soup.select('.wp-block-post-content p')
                    article_content = ' '.join([p.text.strip() for p in article_content_elements])
                    if not article_content:
                        print("Article content is empty. Check selector or page structure.")
                except Exception as e:
                    print(f"Error extracting content: {e}")
                    article_content = "Content extraction failed"
                image_element = soup.select_one('figure.wp-block-post-featured-image > img')
                if image_element:
                    article_image_url = image_element['src']
                else:
                    article_image_url = "Image URL not found"

                retry_attempts = 1
                while retry_attempts > 0:
                    try:
                        driver.get(url)
                        WebDriverWait(driver, 15).until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'header.article__header > div.article__title-wrapper')))
                        break  # Break out of the retry loop if successful
                    except TimeoutException:
                        print("The element did not load within 10 seconds.")
                        retry_attempts -= 1
                        if retry_attempts == 0:
                            continue

                page_source = driver.page_source  # Get the HTML source of the page
                author_soup = BeautifulSoup(page_source, 'html.parser')  # Parse it with BeautifulSoup

                # Now, use BeautifulSoup to find elements as usual
                author_element = author_soup.select_one('div.wp-block-tc23-author-card-name > a')
                if author_element:
                    author = author_element.text.strip()
                else:
                    author = "Author not found"

                try:
                    category_element = driver.find_element(By.CSS_SELECTOR, 'a.is-taxonomy-category')
                    category = category_element.text
                except NoSuchElementException:
                    try:
                        category_element = driver.find_element(By.CSS_SELECTOR, 'a.is-taxonomy-category')
                        category = category_element.text
                    except NoSuchElementException:
                        category = "Category not found"

                tags_elements = driver.find_elements(By.CSS_SELECTOR, 'div.taxonomy-post_tag.wp-block-post-terms a')
                tags = [element.text for element in tags_elements]

                # Save or retrieve the category
                category_obj, _ = Category.objects.get_or_create(name=category)

                # Save or retrieve the author
                author_obj, _ = Author.objects.get_or_create(name=author)

                # Save the article
                # Check if the article already exists to avoid duplicates
                article_obj, created = Article.objects.get_or_create(
                    title=title,
                    defaults={
                        'author': author_obj,
                        'category': category_obj,
                        'publication_date': localized_dt,
                        'content': article_content,
                        'image_url': article_image_url
                    }
                )

                # If the article is newly created, handle the tags
                if created:
                    for tag_name in tags:
                        tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                        ArticleTag.objects.get_or_create(article=article_obj, tag=tag_obj)

                # Print a message indicating success
                self.stdout.write(self.style.SUCCESS(f'Successfully saved article: {title}'))

        except WebDriverException as e:
            self.stdout.write(self.style.ERROR(f"WebDriverException encountered: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
        finally:
            driver.quit()
