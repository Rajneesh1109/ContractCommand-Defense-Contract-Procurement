import hashlib
import time
from django.db import models
from django.conf import settings
from vendors.models import Vendor
from contracts.models import Contract, ContractMilestone

class InspectionCertificate(models.Model):
    STATUS_CHOICES = [
        ('PASSED', 'Accepted / Quality Passed (DD-250 Certified)'),
        ('CONDITIONALLY_PASSED', 'Conditional Acceptance (Minor Rectification)'),
        ('REJECTED', 'Rejected (Defect / Non-Compliance)'),
    ]

    certificate_number = models.CharField(max_length=60, unique=True, help_text="DD-250 / Acceptance Certificate Ref")
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='inspection_certificates')
    milestone = models.ForeignKey(ContractMilestone, on_delete=models.CASCADE, related_name='inspections')
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='signed_inspections')
    inspection_date = models.DateField()
    inspection_location = models.CharField(max_length=150, default='Central Military Quality Directorate Testing Facility')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PASSED')
    qa_report_number = models.CharField(max_length=60, blank=True, help_text="Laboratory / Range Test Report Ref")
    findings_and_notes = models.TextField(help_text="Detailed inspection remarks and test bench readings")
    digital_signature = models.CharField(max_length=128, blank=True, help_text="Cryptographic integrity signature")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.digital_signature:
            raw = f"{self.certificate_number}:{self.contract.contract_number}:{time.time()}"
            self.digital_signature = hashlib.sha256(raw.encode()).hexdigest()
        super().save(*args, **kwargs)
        # Automatically update milestone status
        if self.status == 'PASSED':
            self.milestone.status = 'INSPECTION_PASSED'
            self.milestone.save(update_fields=['status'])

    def __str__(self):
        return f"{self.certificate_number} - {self.contract.contract_number} ({self.get_status_display()})"


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted by Contractor'),
        ('THREE_WAY_MATCH_VERIFIED', '3-Way Match Verified (Contract + DD-250 + Claim)'),
        ('AUDIT_APPROVED', 'Approved by Defense Finance Division'),
        ('PAID', 'Settled & Disbursed'),
        ('DISPUTED', 'Disputed / Audit Inquiry Raised'),
    ]

    invoice_number = models.CharField(max_length=60, unique=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='invoices')
    milestone = models.ForeignKey(ContractMilestone, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='invoices')
    inspection_cert = models.ForeignKey(InspectionCertificate, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    
    invoice_date = models.DateField()
    due_date = models.DateField()
    gross_amount = models.DecimalField(max_digits=15, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    withholding_retention_pct = models.DecimalField(max_digits=5, decimal_places=2, default=5.00, help_text="Standard 5% Defense Warranty Retention")
    withholding_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    net_payable_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    payment_status = models.CharField(max_length=35, choices=STATUS_CHOICES, default='SUBMITTED')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_totals(self):
        gross = float(self.gross_amount or 0)
        retention = gross * (float(self.withholding_retention_pct or 0) / 100.0)
        self.withholding_amount = round(retention, 2)
        net = gross - retention + float(self.tax_amount or 0)
        self.net_payable_amount = round(net, 2)

    def save(self, *args, **kwargs):
        self.calculate_totals()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.vendor.name} - ₹{self.net_payable_amount}"


class PaymentDisbursement(models.Model):
    METHOD_CHOICES = [
        ('DIRECT_TREASURY_TRANSFER', 'Direct Defense Treasury Transfer'),
        ('SBI_GOV_RTGS', 'Reserve Bank / SBI Gov RTGS'),
        ('DEFENSE_ESCROW', 'Defense Escrow Account Release'),
        ('LETTER_OF_CREDIT', 'Irrevocable Letter of Credit (LC)'),
    ]

    disbursement_reference = models.CharField(max_length=60, unique=True, help_text="Treasury Transaction Reference / UTR")
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='disbursements')
    disbursement_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.CharField(max_length=35, choices=METHOD_CHOICES, default='SBI_GOV_RTGS')
    bank_reference = models.CharField(max_length=80, blank=True)
    disbursed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='processed_disbursements')
    remarks = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update invoice status to PAID
        self.invoice.payment_status = 'PAID'
        self.invoice.save(update_fields=['payment_status'])
        # If linked to a milestone, mark milestone as PAID
        if self.invoice.milestone:
            self.invoice.milestone.status = 'PAID'
            self.invoice.milestone.save(update_fields=['status'])

    def __str__(self):
        return f"{self.disbursement_reference} - ₹{self.amount} ({self.get_payment_method_display()})"
