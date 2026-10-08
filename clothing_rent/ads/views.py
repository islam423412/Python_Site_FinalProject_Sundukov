from django.contrib.auth import login
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import models  # <-- ИСПРАВЛЕНО: Добавлен импорт для NameError
from django.db.models import Avg
from django.db.models.query import QuerySet
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

    def get_queryset(self) -> QuerySet:
        query = self.request.GET.get('q')
        location_filter = self.request.GET.get('location')

        ads = Ad.objects.filter(status='published').order_by('-created_at')

        if query:
            ads = ads.filter(title__icontains=query) | ads.filter(description__icontains=query)
        if location_filter:
            ads = ads.filter(location__icontains=location_filter)

        return ads

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['search_location'] = self.request.GET.get('location', '')
        return context


class AdDetailView(DetailView):
    """Детальный просмотр объявления + добавление отзыва"""
    model = Ad
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- РАСЧЕТ ЗВЕЗД (ПЕРЕНЕСЕНО ИЗ HTML) ---
        reviews_count = self.object.reviews.count()

        if reviews_count > 0:
            avg_rating = self.object.reviews.aggregate(
                avg=Avg('rating', output_field=models.FloatField())
            )['avg']

            full_stars = int(round(avg_rating))
            empty_stars = 5 - full_stars

            context['full_stars'] = range(full_stars)
            context['empty_stars'] = range(empty_stars)
            context['reviews_avg'] = round(avg_rating, 1)
        else:
            context['full_stars'] = []
            context['empty_stars'] = range(5)
            context['reviews_avg'] = None
        # --- КОНЕЦ РАСЧЕТА ---

        ad_status_ok = self.object.status == 'published'
        user_authenticated = self.request.user.is_authenticated
        context['show_contact_info'] = ad_status_ok and user_authenticated

        if self.request.method == "POST":
            context['review_form'] = ReviewForm(self.request.POST)
        else:
            context['review_form'] = ReviewForm()

        try:
            self.object.increment_views()
        except AttributeError:
            pass

        return context

    def post(self, request: HttpRequest, *args, **kwargs):
        self.object = self.get_object()
        form = ReviewForm(request.POST)

        if form.is_valid() and request.user.is_authenticated:
            review = form.save(commit=False)
            review.ad = self.object
            review.author = request.user
            review.save()
            return redirect('ad_detail', pk=self.object.pk)

        context = self.get_context_data(review_form=form)
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


def register_view(request: HttpRequest):
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
def moderation_queue(request: HttpRequest):
    """Страница очереди на проверку (только для персонала)"""
    pending_ads = Ad.objects.filter(status='moderation').order_by('-created_at')
    return render(request, 'ads/moderation_queue.html', {'ads': pending_ads})


@staff_member_required
def approve_ad(request: HttpRequest, pk: int):
    """Одобрение объявления (меняет статус на published)"""
    ad = get_object_or_404(Ad, pk=pk)
    ad.status = 'published'
    ad.save()
    return redirect('moderation_queue')


@staff_member_required
def reject_ad(request: HttpRequest, pk: int):
    """Отклонение объявления (меняет статус на draft)"""
    ad = get_object_or_404(Ad, pk=pk)
    ad.status = 'draft'
    ad.save()
    return redirect('moderation_queue')