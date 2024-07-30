from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='vehiclehome'),
    path('about/', views.about, name='vehicleabout'),
    path('services/', views.services, name='vehicleservices'),
    path('contact/', views.contact, name='vehiclecontact'),
    
    # Login views
    path('mechaniclogin/', LoginView.as_view(template_name='vehicle/mechaniclogin.html'), name='mechaniclogin'),
    path('customerlogin/', LoginView.as_view(template_name='vehicle/customerlogin.html'), name='customerlogin'),
    path('adminlogin/', views.admin_login_view, name='adminlogin'),
    
    #  path('adminlogin/', LoginView.as_view(template_name='vehicle/adminlogin.html'), name='adminlogin'),
    
    # Click views
    path('customerclick/', views.customerclick_view, name='customerclick'),
    path('mechanicsclick/', views.mechanicsclick_view, name='mechanicsclick'),
    path('adminclick/', views.adminclick_view, name='adminclick'),
    
    # Signup views
    path('mechanicsignup/', views.mechanic_signup_view, name='mechanicsignup'),
    path('customersignup/', views.customer_signup_view, name='customersignup'),
    
    # Login and logout views
    path('login/', LoginView.as_view(template_name='vehicle/home.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='vehicle/home.html'), name='logout'),
    
    # After login view
    path('afterlogin/', views.afterlogin_view, name='afterlogin'),
    
    path('customer-dashboard/', views.customer_dashboard_view, name='customer-dashboard'),
    path('mechanic-dashboard/', views.mechanic_dashboard_view, name='mechanic-dashboard'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin-dashboard'),
]
