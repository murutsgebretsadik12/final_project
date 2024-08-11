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
from django.core.paginator import Paginator
from django.conf import settings
import requests






# Set up logging
logger = logging.getLogger(__name__)

# static pages

def home(request):
    return render(request, 'vehicle/home.html')

def about(request):
    return render(request, 'vehicle/about.html', {'title': 'about'})

def contact(request):
    context = {
        'garage_lat': 53.360690,
        'garage_lng': -6.278290,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'vehicle/contact.html', context)


def services(request):
    return render(request, 'vehicle/Services.html', {'title': 'services'})


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






#customer based login
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


#mechanic based login
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


#admin based login
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
#Admin based view START
#============================================================================================

# Check if user is admin
def is_admin(user):
    return user.is_staff


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    enquiries = models.Request.objects.select_related('customer').all().order_by('-id')

    context = {
        'total_customer': models.Customer.objects.count(),
        'total_mechanic': models.Mechanic.objects.count(),
        'total_request': models.Request.objects.count(),
        'total_feedback': models.Feedback.objects.count(),
        'data': zip((enq.customer for enq in enquiries), enquiries),
    }

    return render(request, 'vehicle/admin_dashboard.html', context)


@login_required(login_url='adminlogin')
def admin_customer_view(request):
    return render(request,'vehicle/admin_customer.html')



@login_required(login_url='adminlogin')
def admin_view_customer_view(request):
    customers = models.Customer.objects.all()
    return render(request, 'vehicle/admin_view_customer.html', {'customers': customers})

@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('admin-view-customer')

@login_required(login_url='adminlogin')
def update_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,request.FILES,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('admin-view-customer')
    return render(request,'vehicle/update_customer.html',context=mydict)



@login_required(login_url='adminlogin')
def admin_add_customer_view(request):
    userForm = forms.CustomerUserForm()
    customerForm = forms.CustomerForm()
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST)
        customerForm = forms.CustomerForm(request.POST, request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(user.password)
            user.save()

            customer = customerForm.save(commit=False)
            customer.user = user
            if not customer.profile_pic:
                customer.profile_pic = 'profile_pic/CustomerProfilePic/default.jpg'
            customer.save()

            customer_group, created = Group.objects.get_or_create(name='CUSTOMER')
            customer_group.user_set.add(user)

            return HttpResponseRedirect('/admin-view-customer')
    return render(request, 'vehicle/admin_add_customer.html', {'userForm': userForm, 'customerForm': customerForm})


@login_required(login_url='adminlogin')
def admin_view_customer_enquiry_view(request):
    enquiry=models.Request.objects.all().order_by('-id')
    customers=[]
    for enq in enquiry:
        customer=models.Customer.objects.get(id=enq.customer_id)
        customers.append(customer)
    return render(request,'vehicle/admin_view_customer_enquiry.html',{'data':zip(customers,enquiry)})


@login_required(login_url='adminlogin')
def admin_view_customer_invoice_view(request):
    enquiry=models.Request.objects.values('customer_id').annotate(Sum('cost'))
    print(enquiry)
    customers=[]
    for enq in enquiry:
        print(enq)
        customer=models.Customer.objects.get(id=enq['customer_id'])
        customers.append(customer)
    return render(request,'vehicle/admin_view_customer_invoice.html',{'data':zip(customers,enquiry)})



@login_required(login_url='adminlogin')
def admin_mechanic_view(request):
    return render(request,'vehicle/admin_mechanic.html')




@login_required(login_url='adminlogin')
def admin_view_mechanic_view(request):
    mechanics=models.Mechanic.objects.all()
    return render(request,'vehicle/admin_view_mechanic.html',{'mechanics':mechanics})

@login_required(login_url='adminlogin')
def delete_mechanic_view(request,pk):
    mechanic=models.Mechanic.objects.get(id=pk)
    user=models.User.objects.get(id=mechanic.user_id)
    user.delete()
    mechanic.delete()
    return redirect('admin-view-mechanic')

@login_required(login_url='adminlogin')
def update_mechanic_view(request,pk):
    mechanic=models.Mechanic.objects.get(id=pk)
    user=models.User.objects.get(id=mechanic.user_id)
    userForm=forms.MechanicUserForm(instance=user)
    mechanicForm=forms.MechanicForm(request.FILES,instance=mechanic)
    mydict={'userForm':userForm,'mechanicForm':mechanicForm}
    if request.method=='POST':
        userForm=forms.MechanicUserForm(request.POST,instance=user)
        mechanicForm=forms.MechanicForm(request.POST,request.FILES,instance=mechanic)
        if userForm.is_valid() and mechanicForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            mechanicForm.save()
            return redirect('admin-view-mechanic')
    return render(request,'vehicle/update_mechanic.html',context=mydict)

@login_required(login_url='adminlogin')
def admin_add_mechanic_view(request):
    userForm = forms.MechanicUserForm()
    mechanicForm = forms.MechanicForm()
    mechanicSalary = forms.MechanicSalaryForm()
    
    if request.method == 'POST':
        userForm = forms.MechanicUserForm(request.POST)
        mechanicForm = forms.MechanicForm(request.POST, request.FILES)
        mechanicSalary = forms.MechanicSalaryForm(request.POST)
        
        if userForm.is_valid() and mechanicForm.is_valid() and mechanicSalary.is_valid():
            user = userForm.save(commit=False)
            user.set_password(user.password)
            user.save()
            
            mechanic = mechanicForm.save(commit=False)
            mechanic.user = user
            mechanic.status = True
            mechanic.salary = mechanicSalary.cleaned_data['salary']
            mechanic.save()
            
            my_mechanic_group = Group.objects.get_or_create(name='MECHANIC')
            my_mechanic_group[0].user_set.add(user)
            
            return HttpResponseRedirect('admin-view-mechanic')
        else:
            print('Form errors:', userForm.errors, mechanicForm.errors, mechanicSalary.errors)
    
    return render(request, 'vehicle/admin_add_mechanic.html', {
        'userForm': userForm,
        'mechanicForm': mechanicForm,
        'mechanicSalary': mechanicSalary
    })






@login_required(login_url='adminlogin')
def admin_view_mechanic_salary_view(request):
    mechanics=models.Mechanic.objects.all()
    return render(request,'vehicle/admin_view_mechanic_salary.html',{'mechanics':mechanics})



@login_required(login_url='adminlogin')
def admin_approve_mechanic_view(request):
    mechanics=models.Mechanic.objects.all().filter(status=False)
    return render(request,'vehicle/admin_approve_mechanic.html',{'mechanics':mechanics})


@login_required(login_url='adminlogin')
def approve_mechanic_view(request,pk):
    mechanicSalary=forms.MechanicSalaryForm()
    if request.method=='POST':
        mechanicSalary=forms.MechanicSalaryForm(request.POST)
        if mechanicSalary.is_valid():
            mechanic=models.Mechanic.objects.get(id=pk)
            mechanic.salary=mechanicSalary.cleaned_data['salary']
            mechanic.status=True
            mechanic.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-approve-mechanic')
    return render(request,'vehicle/admin_approve_mechanic_details.html',{'mechanicSalary':mechanicSalary})


@login_required(login_url='adminlogin')
def admin_view_mechanic_salary_view(request):
    mechanics=models.Mechanic.objects.all()
    return render(request,'vehicle/admin_view_mechanic_salary.html',{'mechanics':mechanics})


@login_required(login_url='adminlogin')
def update_salary_view(request,pk):
    mechanicSalary=forms.MechanicSalaryForm()
    if request.method=='POST':
        mechanicSalary=forms.MechanicSalaryForm(request.POST)
        if mechanicSalary.is_valid():
            mechanic=models.Mechanic.objects.get(id=pk)
            mechanic.salary=mechanicSalary.cleaned_data['salary']
            mechanic.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-mechanic-salary')
    return render(request,'vehicle/admin_approve_mechanic_details.html',{'mechanicSalary':mechanicSalary})



@login_required(login_url='adminlogin')
def admin_mechanic_attendance_view(request):
    return render(request,'vehicle/admin_mechanic_attendance.html')


@login_required(login_url='adminlogin')
def admin_take_attendance_view(request):
    # Fetch all active mechanics
    mechanics = models.Mechanic.objects.filter(status=True)
    
    if request.method == 'POST':
        form = forms.AttendanceForm(request.POST)
        
        if form.is_valid():
            # Get the list of present statuses and the selected date
            attendances = request.POST.getlist('present_status')
            date = form.cleaned_data['date']
            
            # Ensure the length of attendances matches the number of mechanics
            if len(attendances) != mechanics.count():
                print('Mismatch between number of mechanics and attendance records')
                return redirect('admin-take-attendance')  # Redirect to the same page
            
            # Prepare attendance data for bulk creation
            attendance_objects = []
            for i, status in enumerate(attendances):
                attendance_objects.append(
                    models.Attendance(
                        date=date,
                        present_status=status,
                        mechanic=mechanics[i]
                    )
                )
            
            # Bulk create attendance records
            models.Attendance.objects.bulk_create(attendance_objects)
            
            # Redirect to the attendance view page
            return redirect('admin-view-attendance')
        else:
            print('Form invalid')
    
    # Create an empty form instance
    aform = forms.AttendanceForm()
    
    return render(request, 'vehicle/admin_take_attendance.html', {'mechanics': mechanics, 'aform': aform})


@login_required(login_url='adminlogin')
def admin_view_attendance_view(request):
    form=forms.AskDateForm()
    if request.method=='POST':
        form=forms.AskDateForm(request.POST)
        if form.is_valid():
            date=form.cleaned_data['date']
            attendancedata=models.Attendance.objects.all().filter(date=date)
            mechanicdata=models.Mechanic.objects.all().filter(status=True)
            mylist=zip(attendancedata,mechanicdata)
            return render(request,'vehicle/admin_view_attendance_page.html',{'mylist':mylist,'date':date})
        else:
            print('form invalid')
    return render(request,'vehicle/admin_view_attendance_ask_date.html',{'form':form})


@login_required(login_url='adminlogin')
def admin_request_view(request):
    return render(request,'vehicle/admin_request.html')



@login_required(login_url='adminlogin')
def admin_view_request_view(request):
    enquiries = models.Request.objects.all().order_by('-id')
    customers = []
    for enq in enquiries:
        customer = models.Customer.objects.get(id=enq.customer_id)
        customers.append(customer)
    
    data = zip(customers, enquiries)
    return render(request, 'vehicle/admin_view_request.html', {'data': data})




@login_required(login_url='adminlogin')
def change_status_view(request,pk):
    adminenquiry=forms.AdminApproveRequestForm()
    if request.method=='POST':
        adminenquiry=forms.AdminApproveRequestForm(request.POST)
        if adminenquiry.is_valid():
            enquiry_x=models.Request.objects.get(id=pk)
            enquiry_x.mechanic=adminenquiry.cleaned_data['mechanic']
            enquiry_x.cost=adminenquiry.cleaned_data['cost']
            enquiry_x.status=adminenquiry.cleaned_data['status']
            enquiry_x.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-request')
    return render(request,'vehicle/admin_approve_request_details.html',{'adminenquiry':adminenquiry})


@login_required(login_url='adminlogin')
def admin_delete_request_view(request,pk):
    requests=models.Request.objects.get(id=pk)
    requests.delete()
    return redirect('admin-view-request')


@login_required(login_url='adminlogin')
def admin_add_request_view(request):
    enquiry=forms.RequestForm()
    adminenquiry=forms.AdminRequestForm()
    mydict={'enquiry':enquiry,'adminenquiry':adminenquiry}
    if request.method=='POST':
        enquiry=forms.RequestForm(request.POST)
        adminenquiry=forms.AdminRequestForm(request.POST)
        if enquiry.is_valid() and adminenquiry.is_valid():
            enquiry_x=enquiry.save(commit=False)
            enquiry_x.customer=adminenquiry.cleaned_data['customer']
            enquiry_x.mechanic=adminenquiry.cleaned_data['mechanic']
            enquiry_x.cost=adminenquiry.cleaned_data['cost']
            enquiry_x.status='Approved'
            enquiry_x.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('admin-view-request')
    return render(request,'vehicle/admin_add_request.html',context=mydict)


@login_required(login_url='adminlogin')
def admin_approve_request_view(request):
    enquiry=models.Request.objects.all().filter(status='Pending')
    return render(request,'vehicle/admin_approve_request.html',{'enquiry':enquiry})

@login_required(login_url='adminlogin')
def approve_request_view(request,pk):
    adminenquiry=forms.AdminApproveRequestForm()
    if request.method=='POST':
        adminenquiry=forms.AdminApproveRequestForm(request.POST)
        if adminenquiry.is_valid():
            enquiry_x=models.Request.objects.get(id=pk)
            enquiry_x.mechanic=adminenquiry.cleaned_data['mechanic']
            enquiry_x.cost=adminenquiry.cleaned_data['cost']
            enquiry_x.status=adminenquiry.cleaned_data['status']
            enquiry_x.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-approve-request')
    return render(request,'vehicle/admin_approve_request_details.html',{'adminenquiry':adminenquiry})









@login_required(login_url='adminlogin')
def admin_view_service_cost_view(request):
    enquiry=models.Request.objects.all().order_by('-id')
    customers=[]
    for enq in enquiry:
        customer=models.Customer.objects.get(id=enq.customer_id)
        customers.append(customer)
    print(customers)
    return render(request,'vehicle/admin_view_service_cost.html',{'data':zip(customers,enquiry)})


@login_required(login_url='adminlogin')
def update_cost_view(request,pk):
    updateCostForm=forms.UpdateCostForm()
    if request.method=='POST':
        updateCostForm=forms.UpdateCostForm(request.POST)
        if updateCostForm.is_valid():
            enquiry_x=models.Request.objects.get(id=pk)
            enquiry_x.cost=updateCostForm.cleaned_data['cost']
            enquiry_x.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-view-service-cost')
    return render(request,'vehicle/update_cost.html',{'updateCostForm':updateCostForm})
















@login_required(login_url='adminlogin')
def admin_report_view(request):
    reports=models.Request.objects.all().filter(Q(status="Repairing Done") | Q(status="Released"))
    dict={
        'reports':reports,
    }
    return render(request,'vehicle/admin_report.html',context=dict)


@login_required(login_url='adminlogin')
def admin_feedback_view(request):
    feedback=models.Feedback.objects.all().order_by('-id')
    return render(request,'vehicle/admin_feedback.html',{'feedback':feedback})

#============================================================================================
#Admin based view END
#============================================================================================











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
            return redirect('customer-dashboard')  # Corrected line
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
    customer=models.Customer.objects.get(user_id=request.user.id)
    feedback=forms.FeedbackForm()
    if request.method=='POST':
        feedback=forms.FeedbackForm(request.POST)
        if feedback.is_valid():
            feedback.save()
        else:
            print("form is invalid")
        return render(request,'vehicle/feedback_sent_by_customer.html',{'customer':customer})
    return render(request,'vehicle/customer_feedback.html',{'feedback':feedback,'customer':customer})
    
#============================================================================================
#customer based view END
#============================================================================================

    
    
    
    
    

 
 #============================================================================================
 # mechanic based view   START
#============================================================================================

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


@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def mechanic_work_assigned_view(request):
    mechanic=models.Mechanic.objects.get(user_id=request.user.id)
    works=models.Request.objects.all().filter(mechanic_id=mechanic.id)
    return render(request,'vehicle/mechanic_work_assigned.html',{'works':works,'mechanic':mechanic})


@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def mechanic_update_status_view(request,pk):
    mechanic=models.Mechanic.objects.get(user_id=request.user.id)
    updateStatus=forms.MechanicUpdateStatusForm()
    if request.method=='POST':
        updateStatus=forms.MechanicUpdateStatusForm(request.POST)
        if updateStatus.is_valid():
            enquiry_x=models.Request.objects.get(id=pk)
            enquiry_x.status=updateStatus.cleaned_data['status']
            enquiry_x.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/mechanic-work-assigned')
    return render(request,'vehicle/mechanic_update_status.html',{'updateStatus':updateStatus,'mechanic':mechanic})


@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def mechanic_feedback_view(request):
    mechanic=models.Mechanic.objects.get(user_id=request.user.id)
    feedback=forms.FeedbackForm()
    if request.method=='POST':
        feedback=forms.FeedbackForm(request.POST)
        if feedback.is_valid():
            feedback.save()
        else:
            print("form is invalid")
        return render(request,'vehicle/feedback_sent.html',{'mechanic':mechanic})
    return render(request,'vehicle/mechanic_feedback.html',{'feedback':feedback,'mechanic':mechanic})

@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def mechanic_salary_view(request):
    mechanic=models.Mechanic.objects.get(user_id=request.user.id)
    workdone=models.Request.objects.all().filter(mechanic_id=mechanic.id).filter(Q(status="Repairing Done") | Q(status="Released"))
    return render(request,'vehicle/mechanic_salary.html',{'workdone':workdone,'mechanic':mechanic})



@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def mechanic_attendance_view(request):
    mechanic=models.Mechanic.objects.get(user_id=request.user.id)
    attendaces=models.Attendance.objects.all().filter(mechanic=mechanic)
    return render(request,'vehicle/mechanic_view_attendance.html',{'attendaces':attendaces,'mechanic':mechanic})




@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def mechanic_profile_view(request):
    mechanic=models.Mechanic.objects.get(user_id=request.user.id)
    return render(request,'vehicle/mechanic_profile.html',{'mechanic':mechanic})


@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def edit_mechanic_profile_view(request):
    mechanic=models.Mechanic.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=mechanic.user_id)
    userForm=forms.MechanicUserForm(instance=user)
    mechanicForm=forms.MechanicForm(request.FILES,instance=mechanic)
    mydict={'userForm':userForm,'mechanicForm':mechanicForm,'mechanic':mechanic}
    if request.method=='POST':
        userForm=forms.MechanicUserForm(request.POST,instance=user)
        mechanicForm=forms.MechanicForm(request.POST,request.FILES,instance=mechanic)
        if userForm.is_valid() and mechanicForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            mechanicForm.save()
            return redirect('mechanic-profile')
    return render(request,'vehicle/edit_mechanic_profile.html',context=mydict)




 
 #============================================================================================
 # mechanic based view   END
#============================================================================================



# views.py

def contact_view(request):
    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            # Save the data from the form to the model
            contact_message = models.ContactMessage(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message']
            )
            contact_message.save()  # Save the instance to the database
            return redirect('contact_success')
    else:
        form = forms.ContactForm()

    return render(request, 'vehicle/contact.html', {'form': form})

def contact_success_view(request):
    return render(request, 'vehicle/contact_success.html')

