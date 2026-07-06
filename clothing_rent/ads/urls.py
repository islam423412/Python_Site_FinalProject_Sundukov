from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.ad_list, name='ad_list'),

    path('<int:pk>/', views.ad_detail, name='ad_detail'),


    path('create/', views.ad_create, name='ad_create'),
    path('<int:pk>/edit/', views.ad_edit, name='ad_edit'),


    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]