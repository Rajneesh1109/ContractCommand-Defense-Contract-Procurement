from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AuditLog

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'security_clearance', 'department', 'is_staff')
    list_filter = ('role', 'security_clearance', 'department', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Defense Profile', {'fields': ('role', 'service_id', 'security_clearance', 'department', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Defense Profile', {'fields': ('role', 'service_id', 'security_clearance', 'department', 'phone')}),
    )

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'module', 'target_id', 'ip_address')
    list_filter = ('action', 'module', 'timestamp')
    search_fields = ('target_id', 'target_repr', 'details', 'user__username')
    readonly_fields = ('user', 'action', 'module', 'target_id', 'target_repr', 'details', 'ip_address', 'timestamp')
