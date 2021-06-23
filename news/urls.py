from django.urls import path
from .views import NewsList, NewsDetail, NewsSearch, NewsAdd, NewsEdit, NewsDelete

urlpatterns = [
    path('', NewsList.as_view()),
    path('<int:pk>', NewsDetail.as_view(), name='news_one'),
    path('search', NewsSearch.as_view(), name='news_search'),
    path('add/', NewsAdd.as_view(), name='news_add'),
    path('edit/<int:pk>', NewsEdit.as_view(), name='news_update'),
    path('delete/<int:pk>', NewsDelete.as_view(), name='news_delete'),
]
