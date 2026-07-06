# ads/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Ad, Review
from .forms import AdForm, ReviewForm, UserRegisterForm  # <-- Все формы здесь


# --- ВЬЮХИ ДЛЯ ОБЪЯВЛЕНИЙ ---

def ad_list(request):
    """Функция поиска и отображения списка объявлений"""

    query = request.GET.get('q')
    location_filter = request.GET.get('location')
    price_filter = request.GET.get('price')

    ads = Ad.objects.filter(status='published').order_by('-created_at')

    if query:
        ads = ads.filter(title__icontains=query) | ads.filter(description__icontains=query)
    if location_filter:
        ads = ads.filter(location__icontains=location_filter)
    if price_filter:
        try:
            price_value = float(price_filter)
            ads = ads.filter(price__lte=price_value)
        except (ValueError, TypeError):
            pass

    return render(request, 'ads/ad_list.html', {'ads': ads})


def ad_detail(request, pk):
    """Просмотр одного объявления и добавление отзыва"""
    ad = get_object_or_404(Ad, pk=pk, status='published')

    show_contact_info = ad.status == 'published'

    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.ad = ad
            review.author = request.user
            review.save()
            return redirect('ad_detail', pk=ad.pk)
    else:
        review_form = ReviewForm()

    context = {
        'ad': ad,
        'show_contact_info': show_contact_info,
        'review_form': review_form,
    }
    return render(request, 'ads/ad_detail.html', context)


@login_required
def ad_create(request):
    """Создание нового объявления"""
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.author = request.user
            ad.status = 'moderation'  # Сразу отправляем на модерацию
            ad.save()
            return redirect('ad_list')
    else:
        form = AdForm()
    return render(request, 'ads/ad_form.html', {'form': form})


@login_required
def ad_edit(request, pk):
    """Редактирование или удаление объявления"""
    ad = get_object_or_404(Ad, pk=pk)

    # Проверка прав: только автор может редактировать свое объявление
    if request.user != ad.author and not request.user.is_staff:
        return redirect('ad_detail', pk=ad.pk)

    if request.method == 'POST':
        # Логика удаления (через POST для безопасности)
        if 'delete_button' in request.POST:
            ad.delete()
            return redirect('ad_list')

        # Логика сохранения изменений
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            return redirect('ad_detail', pk=ad.pk)
    else:
        form = AdForm(instance=ad)
    return render(request, 'ads/ad_form.html', {'form': form, 'object': ad})



def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем нового пользователя в базу данных
            return redirect('login')  # Перенаправляем на страницу входа
    else:
        form = UserRegisterForm()
    return render(request, 'ads/register.html', {'form': form})