from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Mechanic, Customer
from crispy_forms.layout import Layout, Field


class MechanicUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MechanicUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Field('first_name'),
            Field('last_name'),
            Field('username'),
            Field('password', type='password')
        )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        }

class MechanicForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MechanicForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Field('address'),
            Field('mobile'),
            Field('skill'),
            Field('profile_pic')
        )

    class Meta:
        model = Mechanic
        fields = ['address', 'mobile', 'skill', 'profile_pic']
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': 'Enter your address'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter your mobile number'}),
            'skill': forms.TextInput(attrs={'placeholder': 'List your skills'}),
        }

class CustomerUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CustomerUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Sign Up'))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        }

class CustomerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'

    class Meta:
        model = Customer
        fields = ['address', 'mobile', 'profile_pic']
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': 'Enter your address'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter your mobile number'}),
        }
        
        
