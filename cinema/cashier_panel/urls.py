from django.urls import path
from . import views

app_name = 'cashier_panel'

urlpatterns = [
    path('', views.CashierDashboardView.as_view(), name='cashier_dashboard'),
    path('session/<int:session_id>/seats/',
         views.SessionSeatSelectionView.as_view(), name='seat_selection'),
    path('session/<int:session_id>/book/<int:row>/<int:place>/',
         views.BookingCreateView.as_view(), name='booking_create'),
    path('booking/success/<slug:order_slug>/',
         views.BookingSuccessView.as_view(), name='booking_success'),
    path('order/confirm/<slug:order_slug>/',
         views.ConfirmOrderView.as_view(), name='confirm_order'),
    path('order/cancel/<slug:order_slug>/',
         views.CancelOrderView.as_view(), name='cancel_order'),
]
