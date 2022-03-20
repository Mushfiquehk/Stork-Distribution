from django import forms 
from store.models import User, UserProfile

class OrderForm(forms.Form):
    last_name = forms.CharField(max_length=255, label="Last Name")
    first_name = forms.CharField(max_length=255, label="First Name")
    email_address = forms.EmailField(required=False)
    phone_number = forms.CharField(max_length=100, label="Phone Number")
    pickup_time = forms.CharField(max_length=100, label="Pickup Time")

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta():
        model = UserProfile 
        fields = ('company_website', 'business_proof')