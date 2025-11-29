from .models import Film
from admin_panel.models import Session
from django.views.generic import ListView, DetailView, TemplateView
from django.utils import timezone
from datetime import timedelta


class FilmListView(ListView):
    model = Film
    template_name = 'films/film_list.html'
    context_object_name = 'films'

    def get_queryset(self):
        today = timezone.now().date()
        queryset = Film.objects.filter(ending__gte=today).order_by('title')

        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(title__iregex=query)

        return queryset


class FilmDetailView(DetailView):
    model = Film
    template_name = 'films/film_detail.html'
    context_object_name = 'film'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class ContactsView(TemplateView):
    template_name = 'films/contacts.html'


class ScheduleView(TemplateView):
    template_name = 'films/schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=13)
        sessions = Session.objects.filter(
            date__range=[start_date, end_date]
        ).select_related('film', 'hall').order_by('date', 'start_time')

        sessions_by_date = {}
        for session in sessions:
            date_str = session.date.strftime('%Y-%m-%d')
            if date_str not in sessions_by_date:
                sessions_by_date[date_str] = []
            sessions_by_date[date_str].append(session)

        dates = []
        for i in range(14):
            current_date = start_date + timedelta(days=i)
            dates.append({
                'date': current_date,
                'sessions': sessions_by_date.get(
                    current_date.strftime('%Y-%m-%d'), [])
            })

        context.update({
            'dates': dates,
            'today': start_date
        })

        return context
