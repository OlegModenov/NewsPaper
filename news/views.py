from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Post, Category, Author
from .filters import PostFilter
from .forms import NewsForm

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin


class NewsList(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-creation_datetime')
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts_amount'] = len(Post.objects.all())
        context['categories'] = Category.objects.all()
        return context


class NewsOfCategory(NewsList):
    def get_queryset(self):
        return Post.objects.filter(category=self.kwargs['category_id'])


class NewsSearch(ListView):
    model = Post
    template_name = 'news_search.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-creation_datetime')
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts_amount'] = len(Post.objects.all())
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['categories'] = Category.objects.all()
        return context


class NewsDetail(DetailView):
    model = Post
    template_name = 'news_one.html'
    context_object_name = 'news_one'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class NewsAdd(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    model = Post
    template_name = 'news_add.html'
    form_class = NewsForm

    # Функция для кастомной валидации полей формы модели
    # def form_valid(self, form):
    #     form = form.save(commit=False)  # создаем форму, но пока не отправляем ее в БД
    #     form.author = Author.objects.get(author=self.request.user)  # добавляем автора (текущего пользователя)
    #     form.save()
    #     return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form = NewsForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = self.request.user.author
            instance.save()
            return redirect(instance)
        return NewsForm(request, 'news/news_add.html', {'form': form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class NewsEdit(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    model = Post
    template_name = 'news_edit.html'
    form_class = NewsForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class NewsDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'news_delete.html'
    context_object_name = 'news_one'
    queryset = Post.objects.all()
    success_url = '/news/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context



