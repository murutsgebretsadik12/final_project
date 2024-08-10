import os
from django.conf import settings
from PIL import Image
import tempfile
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Mechanic, Customer, Request, Attendance, Feedback, ContactMessage
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from vehicle.forms import (MechanicUserForm,MechanicForm,MechanicSalaryForm,CustomerUserForm,CustomerForm,RequestForm,AdminRequestForm,UpdateCostForm,FeedbackForm,AttendanceForm,AskDateForm,ContactForm)
from vehicle.models import Mechanic, Customer
from django.core.files.uploadedfile import SimpleUploadedFile
from vehicle.models import Mechanic, Customer, Request, Feedback


#Test for model
class MechanicModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testmechanic', password='12345')
        self.mechanic = Mechanic.objects.create(
            user=self.user,
            address='123 Mech St',
            mobile='1234567890',
            skill='Engine repair',
            salary=50000,
            status=True
        )

    def test_mechanic_creation(self):
        self.assertTrue(isinstance(self.mechanic, Mechanic))
        self.assertEqual(self.mechanic.__str__(), self.user.first_name)

    def test_mechanic_fields(self):
        self.assertEqual(self.mechanic.address, '123 Mech St')
        self.assertEqual(self.mechanic.mobile, '1234567890')
        self.assertEqual(self.mechanic.skill, 'Engine repair')
        self.assertEqual(self.mechanic.salary, 50000)
        self.assertTrue(self.mechanic.status)

    def test_mechanic_profile_pic(self):
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            
            image = Image.new('RGB', (100, 100))
            image.save(tmp_file, 'JPEG')
            tmp_file.seek(0)

            # Save the image to the mechanic's profile
            self.mechanic.profile_pic.save('test_image.jpg', tmp_file)

        # Refresh the mechanic instance from the database
        self.mechanic.refresh_from_db()

        # Check if the profile pic was saved
        self.assertTrue(self.mechanic.profile_pic)
        self.assertTrue(os.path.exists(self.mechanic.profile_pic.path))

        # Check if the image was resized
        with Image.open(self.mechanic.profile_pic.path) as img:
            self.assertTrue(img.height <= 300 and img.width <= 300)

        # Clean up
        os.unlink(self.mechanic.profile_pic.path)
        os.unlink(tmp_file.name)

class CustomerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testcustomer', password='12345')
        self.customer = Customer.objects.create(
            user=self.user,
            address='456 Cust St',
            mobile='0987654321'
        )

    def test_customer_creation(self):
        self.assertTrue(isinstance(self.customer, Customer))
        self.assertEqual(self.customer.__str__(), self.user.first_name)

    def test_customer_fields(self):
        self.assertEqual(self.customer.address, '456 Cust St')
        self.assertEqual(self.customer.mobile, '0987654321')

class RequestModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.customer = Customer.objects.create(user=self.user, address='789 Test St', mobile='1122334455')
        self.mechanic = Mechanic.objects.create(user=self.user, address='321 Mech St', mobile='5544332211', skill='Brake repair')
        self.request = Request.objects.create(
            category='two wheeler with gear',
            vehicle_no=1234,
            vehicle_name='TestBike',
            vehicle_model='TB2000',
            vehicle_brand='TestBrand',
            problem_description='Test problem',
            customer=self.customer,
            mechanic=self.mechanic,
            status='Pending'
        )

    def test_request_creation(self):
        self.assertTrue(isinstance(self.request, Request))
        self.assertEqual(self.request.__str__(), 'Test problem')

    def test_request_fields(self):
        self.assertEqual(self.request.category, 'two wheeler with gear')
        self.assertEqual(self.request.vehicle_no, 1234)
        self.assertEqual(self.request.vehicle_name, 'TestBike')
        self.assertEqual(self.request.status, 'Pending')

class AttendanceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testmechanic', password='12345')
        self.mechanic = Mechanic.objects.create(user=self.user, address='123 Att St', mobile='9876543210', skill='General repair')
        self.attendance = Attendance.objects.create(
            mechanic=self.mechanic,
            date=timezone.now().date(),
            present_status='Present'
        )

    def test_attendance_creation(self):
        self.assertTrue(isinstance(self.attendance, Attendance))
        self.assertEqual(self.attendance.__str__(), f"{self.mechanic} - {timezone.now().date()} - Present")

class FeedbackModelTest(TestCase):
    def setUp(self):
        self.feedback = Feedback.objects.create(
            submitted_by='Test User',
            message='Great service!'
        )

    def test_feedback_creation(self):
        self.assertTrue(isinstance(self.feedback, Feedback))
        self.assertEqual(self.feedback.__str__(), f"Feedback by Test User on {timezone.now().date()}")

class ContactMessageModelTest(TestCase):
    def setUp(self):
        self.contact_message = ContactMessage.objects.create(
            name='Test Contact',
            email='test@example.com',
            subject='Test Subject',
            message='Test message content'
        )

    def test_contact_message_creation(self):
        self.assertTrue(isinstance(self.contact_message, ContactMessage))
        self.assertEqual(self.contact_message.name, 'Test Contact')
        self.assertEqual(self.contact_message.email, 'test@example.com')



 #============================================================================================
 #forms based Test
#============================================================================================
class MechanicUserFormTest(TestCase):
    def test_mechanic_user_form_valid(self):
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'password': 'testpassword123'
        }
        form = MechanicUserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_mechanic_user_form_invalid(self):
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': '',  # Username is required
            'password': 'testpassword123'
        }
        form = MechanicUserForm(data=form_data)
        self.assertFalse(form.is_valid())

class MechanicFormTest(TestCase):
    def test_mechanic_form_valid(self):
        form_data = {
            'address': '123 Test St',
            'mobile': '1234567890',
            'skill': 'Engine repair'
        }
        form = MechanicForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_mechanic_form_invalid(self):
        form_data = {
            'address': '',  # Address is required
            'mobile': '1234567890',
            'skill': 'Engine repair'
        }
        form = MechanicForm(data=form_data)
        self.assertFalse(form.is_valid())

class MechanicSalaryFormTest(TestCase):
    def test_mechanic_salary_form_valid(self):
        form_data = {'salary': 50000}
        form = MechanicSalaryForm(data=form_data)
        self.assertTrue(form.is_valid())

class CustomerUserFormTest(TestCase):
    def test_customer_user_form_valid(self):
        form_data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': 'janedoe',
            'password': 'testpassword123'
        }
        form = CustomerUserForm(data=form_data)
        self.assertTrue(form.is_valid())

class CustomerFormTest(TestCase):
    def test_customer_form_valid(self):
        form_data = {
            'address': '456 Customer St',
            'mobile': '9876543210'
        }
        form = CustomerForm(data=form_data)
        self.assertTrue(form.is_valid())

class RequestFormTest(TestCase):
    def test_request_form_valid(self):
        form_data = {
            'category': 'two wheeler with gear',
            'vehicle_no': 1234,
            'vehicle_name': 'TestBike',
            'vehicle_model': 'TB2000',
            'vehicle_brand': 'TestBrand',
            'problem_description': 'Test problem'
        }
        form = RequestForm(data=form_data)
        self.assertTrue(form.is_valid())

class AdminRequestFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.customer = Customer.objects.create(user=self.user, address='123 Test St', mobile='1234567890')
        self.mechanic = Mechanic.objects.create(user=self.user, address='456 Mech St', mobile='0987654321', skill='Engine repair')

    def test_admin_request_form_valid(self):
        form_data = {
            'customer': self.customer.id,
            'mechanic': self.mechanic.id,
            'cost': 1000
        }
        form = AdminRequestForm(data=form_data)
        self.assertTrue(form.is_valid())

class UpdateCostFormTest(TestCase):
    def test_update_cost_form_valid(self):
        form_data = {'cost': 1500}
        form = UpdateCostForm(data=form_data)
        self.assertTrue(form.is_valid())

class FeedbackFormTest(TestCase):
    def test_feedback_form_valid(self):
        form_data = {
            'submitted_by': 'Test User',
            'message': 'Great service!'
        }
        form = FeedbackForm(data=form_data)
        self.assertTrue(form.is_valid())

class AttendanceFormTest(TestCase):
    def test_attendance_form_valid(self):
        form_data = {
            'present_status': 'Present',
            'date': '2023-01-01'
        }
        form = AttendanceForm(data=form_data)
        self.assertTrue(form.is_valid())

class AskDateFormTest(TestCase):
    def test_ask_date_form_valid(self):
        form_data = {
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        }
        form = AskDateForm(data=form_data)
        self.assertTrue(form.is_valid())

class ContactFormTest(TestCase):
    def test_contact_form_valid(self):
        form_data = {
            'name': 'Test Contact',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message content'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        
#============================================================================================
  # Customer View based Test
#============================================================================================

