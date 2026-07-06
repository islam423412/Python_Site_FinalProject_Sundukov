# clothing_rent/urls.py

from django.contrib import admin
from django.urls import path, include  # Не забудьте import include!
from django.contrib.auth import views as auth_views  # Встроенные вьюхи авторизации

urlpatterns = [
    path('admin/', admin.site.urls),

    # Подключаем URL-адреса нашего приложения ads с префиксом ''
    path('', include('ads.urls')),

    # Встроенные URL для входа и выхода из системы
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
