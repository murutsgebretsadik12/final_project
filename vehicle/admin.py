# vehicle/admin.py

from django.contrib import admin
from .models import Customer, Mechanic

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'mobile')
    search_fields = ('user__username', 'user__email', 'mobile')

@admin.register(Mechanic)
class MechanicAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'mobile', 'skill', 'status')
    search_fields = ('user__username', 'user__email', 'mobile', 'skill')
    list_filter = ('status',)


