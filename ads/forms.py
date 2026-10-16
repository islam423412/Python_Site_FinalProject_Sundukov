from django import forms
from .models import Ad, Review


# --- ФОРМА СОЗДАНИЯ ОБЪЯВЛЕНИЯ ---
class AdForm(forms.ModelForm):
    """
    Форма для создания и редактирования объявления.
    """

    # Переопределяем поле contact_info, чтобы сделать его текстовой областью
    contact_info = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Пример: Telegram: @username, Телефон: +7999...'
        }),
        label='Контактная информация'
    )

    class Meta:
        model = Ad
        # --- ИСПРАВЛЕНО: Это список в квадратных скобках, а не строка ---
        fields = [
            'title',
            'description',
            'price',
            'location',
            'contact_info',
        ]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }


# --- ФОРМА ДОБАВЛЕНИЯ ОТЗЫВА ---
class ReviewForm(forms.ModelForm):
    """
    Форма для добавления отзыва к объявлению.
    """
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],  # Оценки от 1 до 5
        widget=forms.RadioSelect,
        initial=5,
        label='Оценка'
    )

    class Meta:
        model = Review
        fields = ['text', 'rating']

        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Расскажите о своем опыте аренды...'
            }),
        }