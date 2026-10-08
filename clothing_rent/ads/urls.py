from django.urls import path
from .views import AdListView, AdDetailView, AdCreateView, AdUpdateView, AdDeleteView, register_view, moderation_queue, approve_ad, reject_ad

urlpatterns = [
    path('', AdListView.as_view(), name='ad_list'), # Главная страница
    path('ad/<int:pk>/', AdDetailView.as_view(), name='ad_detail'),
    path('ad/create/', AdCreateView.as_view(), name='ad_create'),
    path('ad/<int:pk>/edit/', AdUpdateView.as_view(), name='ad_edit'),
    path('ad/<int:pk>/delete/', AdDeleteView.as_view(), name='ad_delete'),
    path('register/', register_view, name='register'),
    path('moderate/', moderation_queue, name='moderation_queue'),
    path('moderate/<int:pk>/approve/', approve_ad, name='approve_ad'),
    path('moderate/<int:pk>/reject/', reject_ad, name='reject_ad'),
]