# ads/forms.py

from django import forms
from .models import Ad, Review
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# Форма для создания и редактирования объявления
class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'price', 'location', 'contact_info']

        # Добавим подсказки (плейсхолдеры) для удобства пользователя
        widgets = {
            'description': forms.Textarea(attrs={'placeholder': 'Опишите одежду, состояние...'}),
            'contact_info': forms.TextInput(attrs={'placeholder': 'Телефон или мессенджер'}),
        }


# Форма для добавления отзыва с оценкой
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        # Включаем оба поля: текст и оценку
        fields = ['text', 'rating']


# Форма для регистрации нового пользователя
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()  # Сделаем поле email обязательным

    class Meta:
        model = User
        # Поля, которые пользователь должен заполнить при регистрации
        fields = ['username', 'email', 'password1', 'password2']