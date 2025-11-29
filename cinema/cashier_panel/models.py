from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтвержден'),
        ('cancelled', 'Отменен'),
    ]

    title = models.CharField('Название фильма', max_length=256)
    name = models.CharField('Имя покупателя', max_length=10)
    slug = models.SlugField('Номер билета', unique=True)
    time = models.DateTimeField('Время и дата сеанса')
    hall = models.CharField('Название зала', max_length=256)
    price = models.IntegerField('Цена билета')
    row = models.IntegerField('Ряд')
    place = models.IntegerField('Место')
    session_id = models.IntegerField('ID сеанса')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES,
                              default='pending')
    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    updated_at = models.DateTimeField('Время обновления', auto_now=True)

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-created_at',)

    def save(self, *args, **kwargs):
        if not self.slug:
            count = Order.objects.count()
            self.slug = f"T{count + 1:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.name}"


class Booking(models.Model):
    session_id = models.IntegerField('ID сеанса')
    row = models.IntegerField('Ряд')
    place = models.IntegerField('Место')
    is_booked = models.BooleanField('Забронировано', default=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True,
                              blank=True, related_name='заказ')

    class Meta:
        verbose_name = 'бронь'
        verbose_name_plural = 'Брони'
        unique_together = ('session_id', 'row', 'place')

    def __str__(self):
        return f"Сеанс {self.session_id} - Ряд {self.row} Место {self.place}"
