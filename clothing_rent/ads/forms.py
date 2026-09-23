from django import forms
from .models import Ad, Review


# --- ФОРМА СОЗДАНИЯ ОБЪЯВЛЕНИЯ ---
class AdForm(forms.ModelForm):
    """
    Форма для создания и редактирования объявления.
    Использует виджеты Bootstrap для красивого отображения.
    """

    # Переопределяем поле contact_info, чтобы сделать его текстовой областью (textarea)
    contact_info = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Пример: Telegram: @username, Телефон: +7999...'
        }),
        label='Контактная информация'
    )

    class Meta:
        model = Ad
        fields = [
            'title',
            'description',
            'price',
            'location',
            'contact_info'
            # УДАЛИЛИ СТРОЧКУ С 'image'
        ]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            # Виджет для image тоже можно удалить отсюда
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем класс Bootstrap ко всем полям, если они не переопределены выше
        for field_name in self.fields:
            if field_name != 'contact_info' and field_name != 'image':
                self.fields[field_name].widget.attrs.update({'class': 'form-control'})


# --- ФОРМА ДОБАВЛЕНИЯ ОТЗЫВА ---
class ReviewForm(forms.ModelForm):
    """
    Форма для добавления отзыва к объявлению.
    Рейтинг реализован через RadioSelect (кнопки-переключатели).
    """

    # Явно определяем рейтинг как ChoiceField с радиокнопками
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],  # Оценки от 1 до 5
        widget=forms.RadioSelect,
        initial=5,
        label='Оценка'
    )

    class Meta:
        model = Review
        fields = ['text', 'rating']  # Порядок важен!

        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Расскажите о своем опыте аренды...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем метку у поля text, так как она обычно не нужна над большим полем
        self.fields['text'].label = ''