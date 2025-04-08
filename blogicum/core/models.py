from django.db import models


class CoreModel(models.Model):
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено'
    )
    is_published: models.BooleanField = models.BooleanField(
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.',
        verbose_name='Опубликовано',
    )

    class Meta:
        abstract = True
