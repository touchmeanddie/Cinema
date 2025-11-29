from .models import Hall, Session
from films.models import Film
from .forms import FilmForm, HallForm, SessionForm
from django.views.generic import (ListView, CreateView, UpdateView,
                                  DeleteView, TemplateView, View, FormView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, time, timedelta


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class AdminRedirectView(View):
    def get(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('admin_panel:admin_dashboard')
        return redirect('admin_panel:login')


class AdminLoginView(View):
    def get(self, request):
        return render(request, 'admin_panel/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_panel:admin_dashboard')
        return render(request, 'admin_panel/login.html')


class AdminLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('admin_panel:login')


class DashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = {
            'films_count': Film.objects.count(),
            'halls_count': Hall.objects.count(),
            'sessions_today': Session.objects.filter(date=timezone.now().date()).count(),
            'active_films': Film.objects.filter(ending__gte=timezone.now().date()).count()
        }
        context['film_list'] = Film.objects.all()[:5]
        return context


class FilmListView(AdminRequiredMixin, ListView):
    model = Film
    template_name = 'admin_panel/film_list.html'
    context_object_name = 'films'

    def get_queryset(self):
        return Film.objects.all().order_by('-ending', 'title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        active_films = []
        archive_films = []

        for film in context['films']:
            if film.ending >= today:
                active_films.append(film)
            else:
                archive_films.append(film)

        context['active_films'] = active_films
        context['archive_films'] = archive_films
        context['today'] = today

        return context


class FilmCreateView(AdminRequiredMixin, CreateView):
    model = Film
    form_class = FilmForm
    template_name = 'admin_panel/film_form.html'
    success_url = reverse_lazy('admin_panel:film_list')


class FilmUpdateView(AdminRequiredMixin, UpdateView):
    model = Film
    form_class = FilmForm
    template_name = 'admin_panel/film_form.html'
    success_url = reverse_lazy('admin_panel:film_list')


class FilmDeleteView(AdminRequiredMixin, DeleteView):
    model = Film
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:film_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = 'admin_panel:film_list'
        return context


class HallListView(AdminRequiredMixin, ListView):
    model = Hall
    template_name = 'admin_panel/hall_list.html'
    context_object_name = 'halls'


class HallCreateView(AdminRequiredMixin, CreateView):
    model = Hall
    form_class = HallForm
    template_name = 'admin_panel/hall_create.html'
    success_url = reverse_lazy('admin_panel:hall_list')


class HallUpdateView(AdminRequiredMixin, UpdateView):
    model = Hall
    form_class = HallForm
    template_name = 'admin_panel/hall_edit.html'
    success_url = reverse_lazy('admin_panel:hall_list')


class HallDeleteView(AdminRequiredMixin, DeleteView):
    model = Hall
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:hall_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = 'admin_panel:hall_list'
        return context


class SessionScheduleView(AdminRequiredMixin, FormView):
    template_name = 'admin_panel/session_schedule.html'
    form_class = SessionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'halls': Hall.objects.all(),
            'films': Film.objects.filter(ending__gte=timezone.now().date()),
            'sessions': Session.objects.filter(
                date__range=[timezone.now().date(), timezone.now().date() + timedelta(days=14)]
            ),
            'today': timezone.now().date()
        })

        film_id = self.request.GET.get('film_id')
        hall_id = self.request.GET.get('hall_id')
        date = self.request.GET.get('date')

        if film_id and hall_id and date:
            context.update({
                'selected_film': Film.objects.get(pk=film_id),
                'selected_hall': Hall.objects.get(pk=hall_id),
                'selected_date': datetime.strptime(date, '%Y-%m-%d').date(),
                'available_times': GetTimesView().get_times(
                    Film.objects.get(pk=film_id),
                    Hall.objects.get(pk=hall_id),
                    datetime.strptime(date, '%Y-%m-%d').date()
                )
            })
        return context

    def form_valid(self, form):
        form.save()
        return redirect('admin_panel:session_schedule')


class GetTimesView(AdminRequiredMixin, View):
    def get(self, request):
        hall_id = request.GET.get('hall_id')
        date = request.GET.get('date')
        film_id = request.GET.get('film_id')

        if not all([hall_id, date, film_id]):
            return JsonResponse({'times': []})

        hall = Hall.objects.get(pk=hall_id)
        film = Film.objects.get(pk=film_id)
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        times = self.get_times(film, hall, selected_date)
        return JsonResponse({'times': times})

    def get_times(self, film, hall, selected_date):
        existing_sessions = Session.objects.filter(hall=hall,
                                                   date=selected_date)
        times = []
        current_time = time(10, 0)

        while current_time <= time(22, 0):
            film_minutes = film.time.hour * 60 + film.time.minute
            current_minutes = current_time.hour * 60 + current_time.minute
            end_minutes = current_minutes + film_minutes
            proposed_end = time(end_minutes // 60, end_minutes % 60)

            if proposed_end > time(23, 0):
                break

            conflict = any(
                current_time < session.end_time and proposed_end > session.start_time
                for session in existing_sessions
            )

            if not conflict:
                times.append(current_time.strftime('%H:%M'))

            next_minutes = end_minutes + 30
            if next_minutes >= 23 * 60:
                break
            current_time = time(next_minutes // 60, next_minutes % 60)

        return times


class SessionDeleteView(AdminRequiredMixin, DeleteView):
    model = Session
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:session_schedule')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = 'admin_panel:session_schedule'
        return context
