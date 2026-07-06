# ads/admin.py

from django.contrib import admin
from .models import Ad # Импортируем нашу модель

# Эта строка "регистрирует" модель Ad в админке
# Теперь Django будет знать, что нужно создать для неё раздел управления
admin.site.register(Ad)