from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Quote(models.Model):
    text = models.TextField(unique=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    weight = models.PositiveIntegerField(default=1)
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.text[:50]
