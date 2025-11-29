from .models import Booking, Order
from admin_panel.models import Session
from .forms import BookingForm
from django.views import View
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator


class SessionSeatSelectionView(View):
    def get(self, request, session_id):
        session = get_object_or_404(Session, id=session_id)
        hall = session.hall
        self.create_bookings(session, hall)
        bookings = Booking.objects.filter(session_id=session_id)
        seats_matrix = self.create_seats_matrix(bookings, hall.count_rows,
                                                hall.count_places)

        return render(request, 'cashier_panel/seat_selection.html', {
            'session': session,
            'hall': hall,
            'seats_matrix': seats_matrix,
            'total_rows': range(1, hall.count_rows + 1),
            'seats_per_row': hall.count_places,
        })

    def create_bookings(self, session, hall):
        hall.count_places = hall.count_places
        total_seats = hall.count_rows * hall.count_places

        existing_count = Booking.objects.filter(session_id=session.id).count()

        if existing_count != total_seats:
            Booking.objects.filter(session_id=session.id).delete()
            bookings_to_create = [
                Booking(session_id=session.id, row=row, place=seat,
                        is_booked=False)
                for row in range(1, hall.count_rows + 1)
                for seat in range(1, hall.count_places + 1)
            ]
            Booking.objects.bulk_create(bookings_to_create)

    def create_seats_matrix(self, bookings, rows, seats_per_row):
        return {
            row: {
                seat: bookings.filter(row=row, place=seat).first().is_booked
                for seat in range(1, seats_per_row + 1)
            }
            for row in range(1, rows + 1)
        }


class BookingCreateView(View):
    def get(self, request, session_id, row, place):
        session = get_object_or_404(Session, id=session_id)

        booking = Booking.objects.get(
            session_id=session_id,
            row=row,
            place=place
        )

        initial_data = {
            'title': session.film.title,
            'time': datetime.combine(session.date, session.start_time),
            'hall': session.hall.name,
            'price': session.hall.price,
            'row': row,
            'place': place,
        }

        context = {
            'form': BookingForm(initial=initial_data),
            'session': session,
            'row': row,
            'place': place,
            'booking': booking,
        }
        return render(request, 'cashier_panel/booking_form.html', context)

    def post(self, request, session_id, row, place):
        session = get_object_or_404(Session, id=session_id)

        booking = Booking.objects.get(
            session_id=session_id,
            row=row,
            place=place,
            is_booked=False
        )

        form = BookingForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.session_id = session_id
            order.save()
            booking.is_booked = True
            booking.order = order
            booking.save()

            return redirect('cashier_panel:booking_success',
                            order_slug=order.slug)

        context = {
            'form': form,
            'session': session,
            'row': row,
            'place': place,
        }
        return render(request, 'cashier_panel/booking_form.html', context)


class BookingSuccessView(View):
    def get(self, request, order_slug):
        order = get_object_or_404(Order, slug=order_slug)
        return render(request, 'cashier_panel/booking_success.html',
                      {'order': order})


class CashierDashboardView(View):
    def get(self, request):
        query = request.GET.get('q', '')

        if query:
            orders = Order.objects.filter(title__iregex=query)
            search_mode = True
        else:
            orders = Order.objects.all().order_by('-created_at')[:10]
            search_mode = False

        total_orders = Order.objects.count()
        today_orders = Order.objects.filter(
            created_at__date=datetime.now().date()
        ).count()

        context = {
            'recent_orders': orders,
            'total_orders': total_orders,
            'today_orders': today_orders,
            'query': query,
            'search_mode': search_mode,
        }
        return render(request, 'cashier_panel/cashier_dashboard.html', context)


class ConfirmOrderView(View):
    @method_decorator(require_POST)
    def post(self, order_slug):
        order = get_object_or_404(Order, slug=order_slug)

        if order.status != 'confirmed':
            order.status = 'confirmed'
            order.save()

        return redirect('cashier_panel:cashier_dashboard')


class CancelOrderView(View):
    @method_decorator(require_POST)
    def post(self, order_slug):
        order = get_object_or_404(Order, slug=order_slug)

        if order.status != 'cancelled':
            order.status = 'cancelled'
            order.save()

            if hasattr(order, 'booking'):
                order.booking.is_booked = False
                order.booking.order = None
                order.booking.save()

        return redirect('cashier_panel:cashier_dashboard')
