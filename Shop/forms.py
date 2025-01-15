from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError

# Form for user signup
class Signup_Form(UserCreationForm):
    email = forms.EmailField(required=True) # add email field to signup form

    class Meta:
        model = User # User model is a predefined model by Django
        fields = ['username', 'email', 'password1', 'password2']

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, label='search')

    
class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label="Old Password")
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm New Password")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if new_password != confirm_password:
            raise ValidationError("New password and confirm password do not match.")
        
        return cleaned_data

