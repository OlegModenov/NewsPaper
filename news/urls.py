from django.urls import path
from .views import NewsList, NewsDetail, NewsSearch, NewsCreate, NewsUpdate, NewsDelete

urlpatterns = [
    path('', NewsList.as_view()),
    path('<int:pk>', NewsDetail.as_view(), name='news_one'),
    path('search', NewsSearch.as_view(), name='news_search'),
    path('create/', NewsCreate.as_view(), name='news_create'),
    path('create/<int:pk>', NewsUpdate.as_view(), name='news_update'),
    path('delete/<int:pk>', NewsDelete.as_view(), name='news_delete'),
]
