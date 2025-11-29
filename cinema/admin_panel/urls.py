from django.urls import path
from . import views

app_name = "admin_panel"

urlpatterns = [
    path('', views.AdminRedirectView.as_view(), name='index'),
    path('login/', views.AdminLoginView.as_view(), name='login'),
    path('logout/', views.AdminLogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='admin_dashboard'),

    path('films/', views.FilmListView.as_view(), name='film_list'),
    path('films/create/', views.FilmCreateView.as_view(), name='film_create'),
    path('films/update/<int:pk>/',
         views.FilmUpdateView.as_view(), name='film_update'),
    path('films/delete/<int:pk>/',
         views.FilmDeleteView.as_view(), name='film_delete'),

    path('halls/', views.HallListView.as_view(), name='hall_list'),
    path('halls/create/', views.HallCreateView.as_view(), name='hall_create'),
    path('halls/update/<int:pk>/',
         views.HallUpdateView.as_view(), name='hall_update'),
    path('halls/delete/<int:pk>/',
         views.HallDeleteView.as_view(), name='hall_delete'),

    path('sessions/',
         views.SessionScheduleView.as_view(), name='session_schedule'),
    path('sessions/get-times/',
         views.GetTimesView.as_view(), name='get_times'),
    path('sessions/delete/<int:pk>/',
         views.SessionDeleteView.as_view(), name='session_delete'),
]
