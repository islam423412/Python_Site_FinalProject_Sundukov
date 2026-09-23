from django.urls import path

# Импортируем все представления (View), которые будем использовать
from .views import (
    AdListView,
    AdDetailView,
    AdCreateView,
    AdUpdateView,
    AdDeleteView,
    register_view,
    moderation_queue,
    approve_ad,
    reject_ad,
)

urlpatterns = [
    # Главная страница: Список объявлений с поиском
    # Именно эта строка отвечает за адрес http://127.0.0.1:8000
    path('', AdListView.as_view(), name='ad_list'),

    # Детальный просмотр одного объявления
    path('ad/<int:pk>/', AdDetailView.as_view(), name='ad_detail'),

    # Создание нового объявления
    path('ad/create/', AdCreateView.as_view(), name='ad_create'),

    # Редактирование существующего объявления
    path('ad/<int:pk>/edit/', AdUpdateView.as_view(), name='ad_edit'),

    # Удаление объявления
    path('ad/<int:pk>/delete/', AdDeleteView.as_view(), name='ad_delete'),

    # Регистрация пользователя (с автоматическим входом)
    path('register/', register_view, name='register'),

    # --- ИНТЕРФЕЙС МОДЕРАЦИИ ---
    # Страница очереди на проверку (доступна только персоналу/staff)
    path('moderate/', moderation_queue, name='moderation_queue'),

    # Кнопки одобрения или отклонения внутри списка модерации
    path('moderate/<int:pk>/approve/', approve_ad, name='approve_ad'),
    path('moderate/<int:pk>/reject/', reject_ad, name='reject_ad'),
]