from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from core.models import CoreModel

User = get_user_model()


class ExtendedPostManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                comment_count=models.Count('comments'),
            )
            .order_by('-pub_date')
            .select_related(
                'author',
                'category',
                'location',
            )
        )


class PublishedManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                is_published=True,
            )
        )


class PublishedPostsManager(ExtendedPostManager, PublishedManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                category__is_published=True,
                pub_date__lte=timezone.now(),
            )
        )


class Category(CoreModel):
    title: models.CharField = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
    )
    description: models.TextField = models.TextField(
        verbose_name='Описание',
    )
    slug: models.SlugField = models.SlugField(
        help_text='Идентификатор страницы для URL;'
        ' разрешены символы латиницы, цифры, дефис и подчёркивание.',
        unique=True,
        verbose_name='Идентификатор',
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    objects = models.Manager()
    published = PublishedManager()

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    text: models.TextField = models.TextField(
        verbose_name='Текст комментария',
    )
    author: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )
    post: models.ForeignKey = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='публикация',
    )

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return f'{self.post.title} - {self.created_at.date()}'


class Location(CoreModel):
    name: models.CharField = models.CharField(
        max_length=256,
        verbose_name='Название места',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name


class Post(CoreModel):
    title: models.CharField = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
    )
    text: models.TextField = models.TextField(
        verbose_name='Текст',
    )
    author: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    category: models.ForeignKey = models.ForeignKey(
        'Category',
        null=True,
        on_delete=models.SET_NULL,
        related_name='post',
        verbose_name='Категория',
    )
    image = models.ImageField(
        blank=True,
        verbose_name='Изображение',
    )
    location: models.ForeignKey = models.ForeignKey(
        'Location',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Местоположение',
    )
    pub_date: models.DateTimeField = models.DateTimeField(
        help_text='Если установить дату и время в будущем'
        ' — можно делать отложенные публикации.',
        verbose_name='Дата и время публикации',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    objects = models.Manager()
    extended = ExtendedPostManager()
    published = PublishedPostsManager()

    def __str__(self) -> str:
        return self.title
