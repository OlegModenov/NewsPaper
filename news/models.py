from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"user: {self.user}, rating: {self.rating}"

    def update_rating(self):
        """ суммарный рейтинг каждой статьи автора умножается на 3;
            суммарный рейтинг всех комментариев автора;
            суммарный рейтинг всех комментариев к статьям автора."""

        articles = Post.objects.filter(author__user_id=self.user_id)
        articles_rating = 0
        for article in articles:
            articles_rating += article.rating

        author_comments = Comment.objects.filter(user__id=self.user_id)
        author_comments_rating = 0
        for comment in author_comments:
            author_comments_rating += comment.rating

        articles_comments = Comment.objects.filter(post__author__user_id=self.user_id)
        articles_comments_rating = 0
        for comment in articles_comments:
            articles_comments_rating += comment.rating

        self.rating = articles_rating * 3 + author_comments_rating + articles_comments_rating
        self.save()


class Category(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"title - {self.title}"


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category, through='PostCategory')

    type = models.BooleanField(default=False)  # False - статья, True - новость
    creation_datetime = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def __str__(self):
        type = 'article' if not self.type else 'news'
        return f"{self.title}, rating: {self.rating}, type: {type}"

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f'{self.text[:125]}...'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    text = models.TextField()
    creation_datetime = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"text: {self.text} and rating: {self.rating}"

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
