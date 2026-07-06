# ads/models.py

from django.db import models
from django.contrib.auth.models import User


class Ad(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('moderation', 'На модерации'),
        ('published', 'Опубликовано'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    location = models.CharField(max_length=150)
    contact_info = models.CharField(max_length=150)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='moderation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# --- ИСПРАВЛЕНИЕ НАЧИНАЕТСЯ ЗДЕСЬ ---

# 1. СНАЧАЛА определяем константу RATING_CHOICES
RATING_CHOICES = [
    (1, 'Ужасно'),
    (2, 'Плохо'),
    (3, 'Нормально'),
    (4, 'Хорошо'),
    (5, 'Отлично'),
]


# 2. И только ПОТОМ используем её в классе Review
class Review(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()

    # Теперь Python знает, что такое RATING_CHOICES
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default=3,
    )

    created_at = models.DateTimeField(auto_now_add=True)
