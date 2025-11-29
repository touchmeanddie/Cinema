from django import forms
from films.models import Film
from .models import Hall, Session
from django.utils import timezone


class FilmForm(forms.ModelForm):
    class Meta:
        model = Film
        fields = '__all__'
        widgets = {
            'beginning': forms.DateInput(attrs={'type': 'date'}),
            'ending': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class HallForm(forms.ModelForm):
    class Meta:
        model = Hall
        fields = ['name', 'number', 'price', 'count_rows', 'count_places']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'count_rows': forms.NumberInput(attrs={'class': 'form-control'}),
            'count_places': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['film', 'hall', 'date', 'start_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['film'].queryset = Film.objects.filter(
            ending__gte=timezone.now().date()
        )
