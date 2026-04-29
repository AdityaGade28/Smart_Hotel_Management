from django import forms
from django.utils import timezone
from .models import Booking


class BookingForm(forms.ModelForm):
    coupon_code = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter coupon code (optional)'
    }))

    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'num_guests', 'special_requests', 'coupon_code']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'num_guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'special_requests': forms.Textarea(attrs={'rows': 3, 'class': 'form-control',
                                                       'placeholder': 'Any special requests or notes...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        today = timezone.now().date()

        if check_in and check_in < today:
            raise forms.ValidationError('Check-in date cannot be in the past.')
        if check_in and check_out and check_out <= check_in:
            raise forms.ValidationError('Check-out must be after check-in.')
        return cleaned_data
