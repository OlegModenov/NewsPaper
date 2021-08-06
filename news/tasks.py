from celery import shared_task
from datetime import datetime, timezone, timedelta

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from news.models import Category


@shared_task
def send_to_subscribers():
    """ Рассылает пользователям список статей из тех категорий, на которые они подписаны, за неделю """
    categories = Category.objects.all()
    for category in categories:
        cat_posts = category.post_set.filter(creation_datetime__gt=datetime.now(timezone.utc) - timedelta(days=7))
        print(category, cat_posts)
        if cat_posts:
            subscribers = category.subscribers.all()
            for subscriber in subscribers:
                print(subscriber)
                if subscriber.email:
                    print('отправка...')
                    # Отправка HTML
                    html_content = render_to_string(
                        'mail_week.html', {
                            'category': category,
                            'cat_posts': cat_posts,
                        }
                    )
                    msg = EmailMultiAlternatives(
                        subject='Список новостей за неделю',
                        from_email='pozvizdd@yandex.ru',
                        to=[subscriber.email, 'olegmodenov@gmail.com'],
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
