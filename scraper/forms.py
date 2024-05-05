from django import forms


class ScrapeTechCrunchForm(forms.Form):
    search_term = forms.CharField(label='Enter the search term for scraping', max_length=100)