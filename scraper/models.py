from django.db import models

# Create your models here.


class Keyword(models.Model):
    keyword = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class KeywordSearchResult(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name='search_results')
    created_at = models.DateTimeField(auto_now_add=True)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Author(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Article(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, null=True, blank=True)
    publication_date = models.DateTimeField()
    content = models.TextField()
    image_url = models.URLField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, through='ArticleTag')


class KeywordSearchResultItem(models.Model):
    search_result = models.ForeignKey(KeywordSearchResult, on_delete=models.CASCADE, related_name='items')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='keyword_items')
    created_at = models.DateTimeField(auto_now_add=True)


class ArticleTag(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
