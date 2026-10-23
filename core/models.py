from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'System Administrator'),
        ('PROCUREMENT_OFFICER', 'Defense Procurement Officer'),
        ('CONTRACTING_OFFICER', 'Contracting & Approving Officer'),
        ('DEFENSE_INSPECTOR', 'Quality & Defense Inspector'),
        ('FINANCE_OFFICER', 'Finance & Disbursement Officer'),
        ('AUDITOR', 'Defense Compliance Auditor'),
        ('VENDOR_REP', 'Defense Contractor Representative'),
    ]

    CLEARANCE_CHOICES = [
        ('UNCLASSIFIED', 'Unclassified'),
        ('CONFIDENTIAL', 'Confidential'),
        ('SECRET', 'Secret'),
        ('TOP_SECRET', 'Top Secret (TS/SCI)'),
    ]

    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='PROCUREMENT_OFFICER')
    service_id = models.CharField(max_length=50, blank=True, null=True, help_text="Military/Gov ID or Badge No.")
    security_clearance = models.CharField(max_length=20, choices=CLEARANCE_CHOICES, default='SECRET')
    department = models.CharField(max_length=100, default='Defense Acquisition Directorate')
    phone = models.CharField(max_length=25, blank=True, null=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class AuditLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_entries')
    action = models.CharField(max_length=50)
    module = models.CharField(max_length=50)
    target_id = models.CharField(max_length=100, blank=True, null=True)
    target_repr = models.CharField(max_length=255, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.action} on {self.module} by {self.user or 'System'}"
