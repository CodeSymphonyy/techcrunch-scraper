# Generated by Django 4.2 on 2024-04-27 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0002_article_keyword'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminActionHolder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Admin Action',
                'verbose_name_plural': 'Admin Actions',
                'managed': False,
            },
        ),
    ]
