from django.contrib import admin
from django.urls import path, include

# Импортируем встроенные виды для входа/выхода сразу
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Админ-панель
    path('admin/', admin.site.urls),

    # Подключаем адреса нашего приложения "ads".
    # Пустая строка '' означает, что главная страница сайта — это список объявлений.
    path('', include('ads.urls')),

    # Страницы авторизации Django
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'),
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]