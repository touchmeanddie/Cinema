from django import forms
from .models import Order


class BookingForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'title', 'time', 'hall', 'price', 'row', 'place']
        widgets = {
            'title': forms.HiddenInput(),
            'time': forms.HiddenInput(),
            'hall': forms.HiddenInput(),
            'price': forms.HiddenInput(),
            'row': forms.HiddenInput(),
            'place': forms.HiddenInput(),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваше имя'
            }),
        }
