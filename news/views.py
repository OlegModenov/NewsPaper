from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Post, Category, Author
from .filters import PostFilter
from .forms import NewsForm

from django.db.models.signals import m2m_changed
from django.dispatch import receiver


@receiver(m2m_changed, sender=Post.category.through)
def notify_subscribers(sender, instance, **kwargs):
    action = kwargs['action']
    if action == 'post_add':
        categories = instance.category.all()
        for category in categories:
            subscribers = category.subscribers.all()
            for subscriber in subscribers:
                print(subscriber.email)
                print(instance.get_absolute_url())
                if subscriber.email:
                    # Отправка HTML
                    html_content = render_to_string(
                        'mail.html', {
                            'user': subscriber,
                            'text': f'{instance.text[:50]}',
                            'post': instance,
                        }
                    )
                    msg = EmailMultiAlternatives(
                        subject=f'Здравствуй, {subscriber.username}. Новая статья в твоём любимом разделе!',
                        body=f'{instance.text[:50]}',
                        from_email='pozvizdd@yandex.ru',
                        to=[subscriber.email, 'olegmodenov@gmail.com'],
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                    # # Отправка простого текста
                    # send_mail(
                    #     subject=f'{subscriber.email}',
                    #     message=f'Появился новый пост!\n {client_title}: {client_text[:50]}. \n Ссылка на статью: ',
                    #     from_email='pozvizdd@yandex.ru',
                    #     recipient_list=[subscriber.email, 'olegmodenov@gmail.com'],


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
        return render(request, 'subscribe_category.html', context)


class NewsList(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'news/news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-creation_datetime')
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts_amount'] = len(Post.objects.all())
        context['categories'] = Category.objects.all()
        return context


class NewsOfCategory(NewsList):
    template_name = 'news/news_category.html'

    def get_queryset(self):
        return Post.objects.filter(category=self.kwargs['category_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = None
        return context


class NewsSearch(ListView):
    model = Post
    template_name = 'news/news_search.html'
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
    template_name = 'news/news_one.html'
    context_object_name = 'news_one'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['post_categories'] = self.model.category
        return context


class NewsAdd(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    model = Post
    template_name = 'news/news_add.html'
    form_class = NewsForm

    def post(self, request, *args, **kwargs):
        form = NewsForm(request.POST)
        client_text = request.POST['text']
        client_title = request.POST['title']

        # # Правильная реализация - у поста несколько категорий
        # categories_pk = request.POST.getlist('category')
        # categories = Category.objects.filter(pk__in=categories_pk)
        # print(categories_pk, categories)
        # cat_subscribers = {}  # Словарь {Категория: queryset подписчиков}
        # for cat in categories:
        #     cat_subscribers[cat] = cat.subscribers.all()

        # Более простая реализация (но неверная) - для одной категории у поста
        category_pk = request.POST['category']
        category = Category.objects.get(pk=category_pk)
        subscribers = category.subscribers.all()

        # Если форма прошла валидацию, перенаправляем на страницу созданной новости
        if form.is_valid():
            # назначение текущего пользователя автором поста
            # post = form.save(commit=False)
            # post.author = self.request.user.author
            # post.save()

            post = form.save()
            print(post.category.all())
            # Почему-то на выходе пустой queryset, без категорий

            # # Рассылка почты
            # for subscriber in subscribers:
            #     print(subscriber.email)
            #     if subscriber.email:
            #         # Отправка HTML
            #         html_content = render_to_string(
            #             'mail.html', {
            #                 'user': subscriber,
            #                 'text': client_text[:50],
            #                 'post': post,
            #             }
            #         )
            #         msg = EmailMultiAlternatives(
            #             subject=f'Здравствуй, {subscriber.username}. Новая статья в твоём любимом разделе!',
            #             body=f'{client_text[:50]}',
            #             from_email='pozvizdd@yandex.ru',
            #             to=[subscriber.email, 'olegmodenov@gmail.com'],
            #         )
            #         msg.attach_alternative(html_content, "text/html")
            #         msg.send()
            #
            #         # # Отправка простого текста
            #         # send_mail(
            #         #     subject=f'{subscriber.email}',
            #         #     message=f'Появился новый пост!\n {client_title}: {client_text[:50]}. \n Ссылка на статью: ',
            #         #     from_email='pozvizdd@yandex.ru',
            #         #     recipient_list=[subscriber.email, 'olegmodenov@gmail.com'],
            return redirect(post)

        return NewsForm(request, 'news/news_add.html', {'form': form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class NewsEdit(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    model = Post
    template_name = 'news/news_edit.html'
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
    template_name = 'news/news_delete.html'
    context_object_name = 'news_one'
    queryset = Post.objects.all()
    success_url = '/news/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
