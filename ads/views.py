from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Avg
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import AdForm, ReviewForm
from .models import Ad, Review


class AdListView(ListView):
    """Отображение списка объявлений с поиском"""
    model = Ad
    template_name = 'ads/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 10

    def get_queryset(self):
        """Фильтрация объявлений"""
        query = self.request.GET.get("q")
        location_filter = self.request.GET.get("location")

        # Показываем только опубликованные
        queryset = Ad.objects.filter(status="published").order_by("-created_at")

        if query:
            queryset = queryset.filter(title__icontains=query) | queryset.filter(
                description__icontains=query)

        if location_filter:
            queryset = queryset.filter(location__icontains=location_filter)

        return queryset

    def get_context_data(self, **kwargs):
        """Общие данные контекста для списка объявлений"""
        context = super().get_context_data(**kwargs)

        # В ListView show_contact_info обычно проверяется в цикле шаблона для каждого объекта,
        # но мы можем передать флаг авторизации
        context['user_authenticated'] = self.request.user.is_authenticated

        # Расчёт рейтинга для списка
        ads_to_rate = context.get('ads', []) or context.get('object_list', [])

        for ad in ads_to_rate:
            reviews_count = ad.reviews.count()
            avg_rating = None
            full_stars = []
            empty_stars = list(range(5))

            if reviews_count > 0:
                avg_val = ad.reviews.aggregate(avg=Avg('rating'))['avg']
                if avg_val:
                    avg_rating = round(avg_val, 1)
                    full_stars = list(range(int(round(avg_rating))))
                    empty_stars = list(range(5 - len(full_stars)))

            setattr(ad, '_reviews_avg', avg_rating)
            setattr(ad, '_full_stars', full_stars)
            setattr(ad, '_empty_stars', empty_stars)

        return context


class AdDetailView(DetailView):
    """Детальный просмотр одного объявления"""
    model = Ad
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Проверка прав доступа к контактам
        ad_status_ok = self.object.status == 'published'
        user_authenticated = self.request.user.is_authenticated
        context['show_contact_info'] = ad_status_ok and user_authenticated

        # Формируем форму отзыва
        if self.request.method == "POST":
            context['review_form'] = ReviewForm(self.request.POST)
        else:
            context['review_form'] = ReviewForm()

        # Рассчитываем рейтинг
        reviews_count = self.object.reviews.count()
        avg_rating = None
        full_stars = []
        empty_stars = list(range(5))

        if reviews_count > 0:
            avg_val = self.object.reviews.aggregate(avg=Avg('rating'))['avg']
            if avg_val:
                avg_rating = round(avg_val, 1)
                full_stars = list(range(int(round(avg_rating))))
                empty_stars = list(range(5 - len(full_stars)))

        context.update({
            'reviews_avg': avg_rating,
            'full_stars': full_stars,
            'empty_stars': empty_stars,
        })

        try:
            self.object.increment_views()
        except AttributeError:
            pass

        return context

    def post(self, request, *args, **kwargs):
        """Обработка отправки отзыва"""
        self.object = self.get_object()
        form = ReviewForm(request.POST)

        if form.is_valid() and request.user.is_authenticated:
            review = form.save(commit=False)
            review.ad = self.object
            review.author = request.user
            review.save()
            return redirect('ad_detail', pk=self.object.pk)

        # Если форма не валидна, возвращаем контекст с ошибками
        context = self.get_context_data()
        context['review_form'] = form
        return self.render_to_response(context)


class AdCreateView(LoginRequiredMixin, CreateView):
    """Создание нового объявления"""
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = 'moderation'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ad_list')


class AdUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование своего объявления"""
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.is_staff

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав для редактирования этого объявления.")


class AdDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление своего объявления"""
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'
    success_url = reverse_lazy('ad_list')

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.is_staff

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав для удаления этого объявления.")


# === Функциональные представления (Function Based Views) ===

def register_view(request):
    """Функция регистрации с автоматическим входом"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('ad_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@staff_member_required
def moderation_queue(request):
    """Страница очереди на проверку (только для персонала)"""
    pending_ads = Ad.objects.filter(status='moderation').order_by('-created_at')
    return render(request, 'ads/moderation_queue.html', {'ads': pending_ads})


@staff_member_required
def approve_ad(request, pk):
    """Одобрение объявления"""
    ad = get_object_or_404(Ad, pk=pk)
    ad.status = 'published'
    ad.save()
    return redirect('moderation_queue')


@staff_member_required
def reject_ad(request, pk):
    """Отклонение объявления"""
    ad = get_object_or_404(Ad, pk=pk)
    ad.status = 'draft'
    ad.save()
    return redirect('moderation_queue')