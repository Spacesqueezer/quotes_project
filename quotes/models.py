from django.db import models


class Quote(models.Model):
    # Текст цитаты. Должен быть уникальным
    text = models.TextField(unique=True)

    # Источник цитаты (например, автор или книга)
    source = models.CharField(max_length=255)

    # Вес цитаты для случайного выбора
    weight = models.PositiveIntegerField(default=1)

    # Счётчик просмотров
    views = models.PositiveIntegerField(default=0)

    # Счётчик лайков
    likes = models.PositiveIntegerField(default=0)

    # Счётчик дизлайков
    dislikes = models.PositiveIntegerField(default=0)
