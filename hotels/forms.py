from django import forms
from .models import Hotel, Room


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = [
            'name', 'description', 'address', 'city', 'state', 'country',
            'latitude', 'longitude', 'rating', 'image', 'phone', 'email',
            'amenities', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'amenities': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'WiFi, Pool, Gym, Parking, Restaurant'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ['description', 'address', 'amenities', 'is_active']:
                field.widget.attrs['class'] = 'form-control'
        self.fields['is_active'].widget.attrs['class'] = 'form-check-input'


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'hotel', 'room_number', 'room_type', 'price_per_night',
            'capacity', 'description', 'amenities', 'image', 'floor', 'is_available'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'amenities': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'AC, TV, Minibar, Balcony'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ['description', 'amenities', 'is_available']:
                field.widget.attrs['class'] = 'form-control'
        self.fields['room_type'].widget.attrs['class'] = 'form-select'
        self.fields['hotel'].widget.attrs['class'] = 'form-select'
        self.fields['is_available'].widget.attrs['class'] = 'form-check-input'


class HotelFilterForm(forms.Form):
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Search by city...'
    }))
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Min price'
    }))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Max price'
    }))
    min_rating = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': 'Min rating (0-5)', 'step': '0.1'
    }))
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Default (Recommended)'),
            ('price_asc', 'Price: Low to High'),
            ('price_desc', 'Price: High to Low'),
            ('rating', 'Highest Rating'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
