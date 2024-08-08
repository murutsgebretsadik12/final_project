from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout, Field
from .models import Mechanic, Customer, Request, Feedback




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

   
class MechanicSalaryForm(forms.ModelForm):
    class Meta:
        model = Mechanic
        fields = ['salary'] 
        
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
        
    


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = [
            'category',
            'vehicle_no',
            'vehicle_name',
            'vehicle_model',
            'vehicle_brand',
            'problem_description'
        ]
        widgets = {
            'problem_description': forms.Textarea(attrs={'rows': 3}),
            'vehicle_no': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget = forms.Select(choices=Request.CATEGORY_CHOICES)
        # self.fields['status'].widget = forms.HiddenInput()  # Hide the status field if it's not editable


class AdminRequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['customer', 'mechanic', 'cost']

class UpdateCostForm(forms.Form):
    cost=forms.IntegerField()






class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['submitted_by', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }

#for Attendance related form
presence_choices=(('Present','Present'),('Absent','Absent'))
class AttendanceForm(forms.Form):
    present_status=forms.ChoiceField( choices=presence_choices)
    date=forms.DateField()
    
class AskDateForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))    
    
# forms.py
from django import forms



class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
