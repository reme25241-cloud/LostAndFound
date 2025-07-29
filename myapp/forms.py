from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class BootstrapFormMixin:
    """Mixin to add Bootstrap classes automatically."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = existing_class + ' form-control'

class UserSignupForm(UserCreationForm, BootstrapFormMixin):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ProfileForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = Profile
        fields = ['name', 'email', 'contact', 'age', 'gender', 'address', 'profile_picture']
        widgets = {
            'email': forms.EmailInput(),
            'contact': forms.TextInput(),
            'age': forms.NumberInput(),
            'gender': forms.Select(),
            'name': forms.TextInput(),
            'address': forms.Textarea(attrs={'rows': 3}),
            'profile_picture': forms.FileInput(),
            
        }

# feedback

from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your feedback here...'}),
        }
# myapp/forms.py
from django import forms
from .models import LostItem, FoundReport

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import LostItem
from django import forms
from django import forms
from .models import LostItem
from django.forms.widgets import DateInput


class LostItemForm(forms.ModelForm):
    class Meta:
        model = LostItem
        fields = [
            'full_name',
            'date_lost',
            'location_lost',
            'item_category',
            'item_description',
            'item_photo',
            'contact_info',
        ]
        widgets = {
            'date_lost': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'location_lost': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Library'}),
            'item_category': forms.Select(attrs={'class': 'form-select'}),
            'item_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the lost item'}),
            'item_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email or Phone Number'}),
        }


class MarkAsFoundForm(forms.ModelForm):
    class Meta:
        model = LostItem
        fields = ['is_found']
        widgets = {
            'is_found': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# Optional: For future enhancements
class SearchLostItemForm(forms.Form):
    keyword = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by location, category, or description...'
        })
    )
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + LostItem.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )



class FoundReportForm(forms.ModelForm):
    date_found = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time_found = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = FoundReport
        fields = [
            'finder_name', 'contact_number', 'address',
            'location_found', 'date_found', 'time_found',
            'found_photo'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }
