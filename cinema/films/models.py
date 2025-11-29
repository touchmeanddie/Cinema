from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Film(models.Model):
    AGE_LIMIT_CHOICES = [
        (0, '0+'),
        (6, '6+'),
        (12, '12+'),
        (16, '16+'),
        (18, '18+'),
    ]

    title = models.CharField('Название', max_length=256)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Номер фильма',
        unique=True,
        blank=True
    )
    time = models.TimeField('Длительность фильма')
    country = models.CharField('Страна происхождения', max_length=256)
    beginning = models.DateField('Начало показа')
    ending = models.DateField('Конец показа')
    age_limit = models.IntegerField(
        'Возрастное ограничение',
        choices=AGE_LIMIT_CHOICES,
        default=0
    )
    poster = models.ImageField(
        'Афиша',
        upload_to='posters/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'фильм'
        verbose_name_plural = 'Фильмы'
        ordering = ('title',)

    def save(self, *args, **kwargs):
        if not self.slug:
            count = Film.objects.count()
            base_slug = str(count + 1)
            self.slug = base_slug
            original_slug = self.slug
            counter = 1
            while Film.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
