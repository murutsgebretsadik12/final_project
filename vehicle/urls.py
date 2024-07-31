from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    
    path('customer-profile/', views.customer_profile_view,name='customer-profile'),
    path('edit-customer-profile', views.edit_customer_profile_view,name='edit-customer-profile'),
    path('customer-feedback', views.customer_feedback_view,name='customer-feedback'), 
    # path('feedback-sent', views.feedback_sent_view, name='feedback-sent'), 

    
    path('customer-dashboard', views.customer_dashboard_view, name='customer-dashboard'),
    path('customer-request', views.customer_request_view,name='customer-request'),
    path('customer-add-request/',views.customer_add_request_view,name='customer-add-request'),
    path('customer-view-request',views.customer_view_request_view,name='customer-view-request'),
    path('customer-delete-request/<int:pk>', views.customer_delete_request_view,name='customer-delete-request'),
    path('customer-view-approved-request',views.customer_view_approved_request_view,name='customer-view-approved-request'),
    path('customer-invoice', views.customer_invoice_view,name='customer-invoice'),
    path('customer-view-approved-request-invoice',views.customer_view_approved_request_invoice_view,name='customer-view-approved-request-invoice'),
    
    
    
    path('mechanic-dashboard/', views.mechanic_dashboard_view, name='mechanic-dashboard'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin-dashboard'),
      
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)