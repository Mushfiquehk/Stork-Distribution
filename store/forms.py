from django import forms
from store.models import User, Customer


class OrderForm(forms.Form):
    last_name = forms.CharField(max_length=255, label="Last Name")
    first_name = forms.CharField(max_length=255, label="First Name")
    email_address = forms.EmailField(required=True)
    phone_number = forms.CharField(
        max_length=100, label="Phone Number", required=True)
    address_line_1 = forms.CharField(max_length=500, label="Address Line 1")
    address_line_2 = forms.CharField(
        max_length=500, label="Address Line 2", required=False)


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta():
        model = Customer
        fields = ('website', 'certificates')


class SearchForm(forms.Form):
    search_text = forms.CharField(label="search_text")
