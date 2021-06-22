from django.urls import path
from .views import NewsList, NewsDetail, NewsSearch

urlpatterns = [
    path('', NewsList.as_view()),
    path('<int:pk>', NewsDetail.as_view()),
    path('search', NewsSearch.as_view())
]
