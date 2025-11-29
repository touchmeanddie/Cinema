from django.urls import path
from . import views

app_name = "films"

urlpatterns = [
    path('', views.FilmListView.as_view(), name='film_list'),
    path('film/<slug:slug>/', views.FilmDetailView.as_view(),
         name='film_detail'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('schedule/', views.ScheduleView.as_view(), name='schedule'),
]
