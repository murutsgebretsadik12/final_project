import os
from PIL import Image
from django.db import models
from django.contrib.auth.models import User

class Mechanic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=500)
    mobile = models.CharField(max_length=20)
    skill = models.CharField(max_length=500)
    salary = models.PositiveIntegerField(null=True, blank=True)
    status = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to='profile_pic/MechanicProfilePic/', null=True, blank=True)

    def __str__(self):
        return self.user.first_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.profile_pic and os.path.isfile(self.profile_pic.path):
            img = Image.open(self.profile_pic.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_pic.path)            

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=500)
    mobile = models.CharField(max_length=20)
    profile_pic = models.ImageField(upload_to='profile_pic/CustomerProfilePic/', null=True, blank=True)

    def __str__(self):
        return self.user.first_name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.profile_pic and os.path.isfile(self.profile_pic.path):
            img = Image.open(self.profile_pic.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_pic.path)
                
        
        
                
                
class Request(models.Model):
    CATEGORY_CHOICES = (
        ('two wheeler with gear', 'Two Wheeler with Gear'),
        ('two wheeler without gear', 'Two Wheeler without Gear'),
        ('three wheeler', 'Three Wheeler'),
        ('four wheeler', 'Four Wheeler')
    )
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Repairing', 'Repairing'),
        ('Repairing Done', 'Repairing Done'),
        ('Released', 'Released')
    )
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    vehicle_no = models.PositiveIntegerField()
    vehicle_name = models.CharField(max_length=40)
    vehicle_model = models.CharField(max_length=40)
    vehicle_brand = models.CharField(max_length=40)
    problem_description = models.CharField(max_length=500)
    date = models.DateField(auto_now_add=True)
    cost = models.PositiveIntegerField(null=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    mechanic = models.ForeignKey('Mechanic', on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return self.problem_description

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('On Leave', 'On Leave'),
        ('Late', 'Late')
    )
    
    mechanic = models.ForeignKey('Mechanic', on_delete=models.CASCADE, null=True)
    date = models.DateField()
    present_status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.mechanic} - {self.date} - {self.present_status}"

class Feedback(models.Model):
    date = models.DateField(auto_now_add=True)
    submitted_by = models.CharField(max_length=40)
    message = models.CharField(max_length=500)

    def __str__(self):
        return f"Feedback by {self.submitted_by} on {self.date}"

                


