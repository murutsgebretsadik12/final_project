import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group
from .forms import MechanicUserForm, MechanicForm, CustomerUserForm, CustomerForm
from .models import Customer, Mechanic
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required,user_passes_test
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q, Sum
from . import forms, models




# Set up logging
logger = logging.getLogger(__name__)

# static pages

def home(request):
    return render(request, 'vehicle/home.html')

def about(request):
    return render(request, 'vehicle/about.html', {'title': 'about'})

def contact(request):
    return render(request, 'vehicle/contact.html', {'title': 'contact'})

def services(request):
    return render(request, 'vehicle/services.html', {'title': 'services'})


# Role based redirect

def customerclick_view(request):
    if request.user.is_authenticated:
        if is_customer(request.user):
            return redirect('customer-dashboard')
        else:
            return redirect('afterlogin')
    return render(request, 'vehicle/customerclick.html')

def mechanicsclick_view(request):
    if request.user.is_authenticated:
        if is_mechanic(request.user):
            return redirect('mechanic-dashboard')
        else:
            return redirect('afterlogin')
    return render(request, 'vehicle/mechanicsclick.html')

    
@login_required(login_url='adminlogin')
def adminclick_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_mechanic(request.user):
        return redirect('mechanic-dashboard')
    elif is_customer(request.user):
        return redirect('customer-dashboard')
    else:
        return redirect('customer-dashboard')  # Default fallback to customer-dashboard
    
    
    

#User based registeration

def mechanic_signup_view(request):
    userForm = MechanicUserForm()
    mechanicForm = MechanicForm()

    if request.method == 'POST':
        userForm = MechanicUserForm(request.POST)
        mechanicForm = MechanicForm(request.POST, request.FILES)

        if userForm.is_valid() and mechanicForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(user.password)
            user.save()

            mechanic = mechanicForm.save(commit=False)
            mechanic.user = user

            if not mechanic.profile_pic:
                mechanic.profile_pic = 'profile_pic/MechanicProfilePic/default.jpg'
            mechanic.save()

            my_mechanic_group, created = Group.objects.get_or_create(name='MECHANIC')
            my_mechanic_group.user_set.add(user)

            logger.info("Mechanic account created successfully.")
            return redirect('mechaniclogin')
        else:
            logger.error("Form validation failed. User form errors: %s, Mechanic form errors: %s", userForm.errors, mechanicForm.errors)

    context = {'userForm': userForm, 'mechanicForm': mechanicForm}
    return render(request, 'vehicle/mechanicsignup.html', context)

def customer_signup_view(request):
    if request.method == 'POST':
        userForm = CustomerUserForm(request.POST)
        customerForm = CustomerForm(request.POST, request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(user.password)
            user.save()
            customer = customerForm.save(commit=False)
            customer.user = user
            if not customer.profile_pic:
                customer.profile_pic = 'profile_pic/CustomerProfilePic/default.jpg'
            customer.save()
            my_customer_group, created = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group.user_set.add(user)
            return redirect('customerlogin')
    else:
        userForm = CustomerUserForm()
        customerForm = CustomerForm()
        
    context = {'userForm': userForm, 'customerForm': customerForm}
    return render(request, 'vehicle/customersignup.html', context)






#user based login
def customer_login_view(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if is_customer(user):
                    login(request, user)
                    logger.info("Customer %s logged in successfully.", username)
                    return redirect('customer-dashboard')
                else:
                    logger.warning("Login attempt with non-customer account by %s.", username)
                    return render(request, 'vehicle/customerlogin.html', {'form': form, 'error': 'Invalid login credentials'})
            else:
                logger.warning("Invalid login attempt by %s.", username)
                return render(request, 'vehicle/customerlogin.html', {'form': form, 'error': 'Invalid login credentials'})
    return render(request, 'vehicle/customerlogin.html', {'form': form})



def mechanic_login_view(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if is_mechanic(user):
                    login(request, user)
                    logger.info("Mechanic %s logged in successfully.", username)
                    return redirect('afterlogin')
                else:
                    logger.warning("Login attempt with non-mechanic account by %s.", username)
                    return render(request, 'vehicle/mechaniclogin.html', {'form': form, 'error': 'Invalid login credentials'})
            else:
                logger.warning("Invalid login attempt by %s.", username)
                return render(request, 'vehicle/mechaniclogin.html', {'form': form, 'error': 'Invalid login credentials'})
    return render(request, 'vehicle/mechaniclogin.html', {'form': form})



def admin_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_staff:  # Checking if the user is a staff member
                    login(request, user)
                    return redirect('admin-dashboard')
                else:
                    form.add_error(None, 'You are not authorized to access the admin area.')
    else:
        form = AuthenticationForm()
    return render(request, 'vehicle/adminlogin.html', {'form': form})







#Helper function and decorater

def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()

def is_mechanic(user):
    return user.groups.filter(name='MECHANIC').exists()

def is_admin(user):
    return user.groups.filter(name='Admin').exists()


def admin_required(function=None):
    actual_decorator = user_passes_test(is_admin)
    if function:
        return actual_decorator(function)
    return actual_decorator







    

#Dashboard view
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_dashboard_view(request):
    customer = Customer.objects.get(user_id=request.user.id)
    # Fetch and calculate relevant data for the customer dashboard
    context = {
        'customer': customer,
        # Add more context variables as needed
    }
    return render(request, 'vehicle/customer_dashboard.html', context)



@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def mechanic_dashboard_view(request):
    mechanic = Mechanic.objects.get(user_id=request.user.id)
    # Fetch and calculate relevant data for the mechanic dashboard
    context = {
        'mechanic': mechanic,
        # Add more context variables as needed
    }
    return render(request, 'vehicle/mechanic_dashboard.html', context)



# Check if user is admin
def is_admin(user):
    return user.is_staff


@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    # Fetch relevant data for the admin dashboard
    context = {
        # Add context variables as needed
    }
    return render(request, 'vehicle/admin_dashboard.html', context)



    
    
    
@login_required
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-dashboard')
    elif is_mechanic(request.user):
        return redirect('mechanic-dashboard')
    elif is_admin(request.user):
        return redirect('admin-dashboard')
    else:
        return redirect('vehiclehome')
    


def logout_view(request):
    logout(request)
    return redirect('vehiclehome')











#============================================================================================
#customer based view START
#============================================================================================

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_dashboard_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    work_in_progress = models.Request.objects.filter(customer_id=customer.id, status='Repairing').count()
    work_completed = models.Request.objects.filter(customer_id=customer.id).filter(Q(status="Repairing Done") | Q(status="Released")).count()
    new_request_made = models.Request.objects.filter(customer_id=customer.id).filter(Q(status="Pending") | Q(status="Approved")).count()
    bill = models.Request.objects.filter(customer_id=customer.id).filter(Q(status="Repairing Done") | Q(status="Released")).aggregate(Sum('cost'))
    
    context = {
        'work_in_progress': work_in_progress,
        'work_completed': work_completed,
        'new_request_made': new_request_made,
        'bill': bill['cost__sum'] if bill['cost__sum'] is not None else 0,
        'customer': customer,
    }
    return render(request, 'vehicle/customer_dashboard.html', context=context)


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_profile_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    return render(request, 'vehicle/customer_profile.html', {'customer': customer})



@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_customer_profile_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    user = models.User.objects.get(id=customer.user_id)
    userForm = forms.CustomerUserForm(instance=user)
    customerForm = forms.CustomerForm(instance=customer)
    
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST, instance=user)
        customerForm = forms.CustomerForm(request.POST, request.FILES, instance=customer)
        
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save(commit=False)
            if user.password:
                user.set_password(user.password)  # Ensure password is hashed
            user.save()
            customerForm.save()
            return HttpResponseRedirect('customer-profile')
    
    context = {
        'userForm': userForm,
        'customerForm': customerForm,
    }
    
    return render(request, 'vehicle/edit_customer_profile.html', context)







@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_add_request_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    if request.method == 'POST':
        form = forms.RequestForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.customer = customer
            enquiry.save()
            return HttpResponseRedirect('customer-dashboard')
    else:
        form = forms.RequestForm()
    return render(request, 'vehicle/customer_add_request.html', {'form': form, 'customer': customer})

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_request_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'vehicle/customer_request.html',{'customer':customer})



@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_view_request_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    enquiries = models.Request.objects.filter(customer_id=customer.id, status="Pending")
    return render(request, 'vehicle/customer_view_request.html', {'customer': customer, 'enquiries': enquiries})



@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_delete_request_view(request, pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    enquiry = get_object_or_404(models.Request, id=pk, customer_id=customer.id, status='Pending')
    enquiry.delete()
    return redirect(reverse('customer-view-request'))


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_view_approved_request_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    enquiries = models.Request.objects.filter(customer_id=customer.id).exclude(status='Pending')
    return render(request, 'vehicle/customer_view_approved_request.html', {'customer': customer, 'enquiries': enquiries})

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_view_approved_request_invoice_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    enquiries=models.Request.objects.all().filter(customer_id=customer.id).exclude(status='Pending')
    return render(request,'vehicle/customer_view_approved_request_invoice.html',{'customer':customer,'enquiries':enquiries})


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_invoice_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    enquiries = models.Request.objects.filter(customer_id=customer.id).exclude(status='Pending')
    return render(request, 'vehicle/customer_invoice.html', {'customer': customer, 'enquiries': enquiries})



@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_feedback_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    if request.method == 'POST':
        feedback_form = forms.FeedbackForm(request.POST)
        if feedback_form.is_valid():
            feedback = feedback_form.save(commit=False)
            feedback.customer = customer  # Associate feedback with the current customer
            feedback.save()
            return redirect('feedback-sent')  # Redirect to feedback confirmation page
    else:
        feedback_form = forms.FeedbackForm()
    
    return render(request, 'vehicle/customer_feedback.html', {
        'feedback_form': feedback_form,
        'customer': customer
    })
    
#============================================================================================
#customer based view END
#============================================================================================

    

 
 #============================================================================================
 # mechanic based view   START
#============================================================================================
