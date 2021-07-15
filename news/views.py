from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import Post, Category, Author
from .filters import PostFilter
from .forms import NewsForm


class SubscribeView(LoginRequiredMixin, View):

    # связывает объекты категории и текущего пользователя
    def get(self, request, category_id, *args, **kwargs):
        user = self.request.user
        category = Category.objects.get(pk=category_id)
        if not category.subscribers.filter(pk=user.pk):
            is_subscriber = False
            category.subscribers.add(user)
        else:
            is_subscriber = True

        context = {
            'categories': Category.objects.all(),
            'category': Category.objects.get(pk=category_id),
            'is_subscriber': is_subscriber
        }
        print(is_subscriber)
        return render(request, 'subscribe_category.html', context)

    # def post(self, request, *args, **kwargs):
    #     user = self.request.user
    #     print(user)
    #     return render(request, 'subscribe_category.html', context)


class NewsList(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-creation_datetime')
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts_amount'] = len(Post.objects.all())
        context['categories'] = Category.objects.all()
        return context


class NewsOfCategory(NewsList):
    template_name = 'news_category.html'

    def get_queryset(self):
        return Post.objects.filter(category=self.kwargs['category_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = None
        return context


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
        context['post_categories'] = self.model.category
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




