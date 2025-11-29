from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import datetime, time, timedelta

User = get_user_model()


class Hall(models.Model):
    number = models.IntegerField('Номер зала', unique=True)
    name = models.CharField('Название зала', max_length=100, default='')
    count_rows = models.IntegerField('Количество рядов', default=10)
    count_places = models.IntegerField('Количество мест в ряду', default=10)
    price = models.IntegerField('Цена билета', default=500)

    class Meta:
        verbose_name = 'зал'
        verbose_name_plural = 'Залы'
        ordering = ('number',)

    def __str__(self):
        return f"{self.number}. {self.name}" if self.name else f"Зал {self.number}"


class Session(models.Model):
    film = models.ForeignKey(
        'films.Film',
        on_delete=models.CASCADE,
        verbose_name='Фильм'
    )
    hall = models.ForeignKey(
        Hall,
        on_delete=models.CASCADE,
        verbose_name='Зал'
    )
    date = models.DateField('Дата сеанса')
    start_time = models.TimeField('Время начала')
    end_time = models.TimeField('Время окончания', blank=True, null=True)

    class Meta:
        verbose_name = 'сеанс'
        verbose_name_plural = 'Сеансы'
        ordering = ('date', 'start_time')
        unique_together = ('hall', 'date', 'start_time')

    def __str__(self):
        return f"{self.film.title} - {self.hall.name} - {self.date} {self.start_time}"

    def clean(self):
        if self.start_time < time(10, 0) or self.start_time > time(23, 0):
            raise ValidationError('Кинотеатр работает с 10:00 до 23:00')

        if self.film.time:
            film_duration = timedelta(
                hours=self.film.time.hour,
                minutes=self.film.time.minute
            )
            start_datetime = datetime.combine(self.date, self.start_time)
            end_datetime = start_datetime + film_duration + timedelta(minutes=30)
            self.end_time = end_datetime.time()

            if end_datetime.time() > time(1, 0) and end_datetime.hour != 0:
                next_day_end = datetime.combine(self.date + timedelta(days=1),
                                                time(1, 0))
                if end_datetime > next_day_end:
                    raise ValidationError('Сеанс должен заканчиваться до 01:00')

        overlapping_sessions = Session.objects.filter(
            hall=self.hall,
            date=self.date
        ).exclude(pk=self.pk)

        for session in overlapping_sessions:
            if (self.start_time < session.end_time and
                    self.end_time > session.start_time):
                raise ValidationError(
                    f'Сеанс пересекается с существующим сеансом: {session}'
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
