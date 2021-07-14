from django import forms
from .models import Post


class NewsForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'category']
        widgets = {
            'title': forms.TextInput(attrs={"class": "form-control"}),
            'text': forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            'category': forms.SelectMultiple(attrs={"class": "form-control", "empty_label": 'sd'}),
        }
        labels = {
            'category': 'Категория'
        }
