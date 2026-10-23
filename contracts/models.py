from django.db import models
from django.conf import settings
from vendors.models import Vendor
from procurement.models import TenderRFP, DefenseItemCatalog

class Contract(models.Model):
    CLASSIFICATION_CHOICES = [
        ('UNCLASSIFIED', 'Unclassified'),
        ('CONFIDENTIAL', 'Confidential'),
        ('SECRET', 'Secret'),
        ('TOP_SECRET', 'Top Secret (TS/SCI)'),
    ]

    STATUS_CHOICES = [
        ('DRAFT', 'Draft Phase'),
        ('LEGAL_TECH_REVIEW', 'Legal & Security Review'),
        ('APPROVED', 'Approved by Contracting Authority'),
        ('ACTIVE', 'Active & Operational Execution'),
        ('AMENDED', 'Active (Amended)'),
        ('COMPLETED', 'Completed & Closed'),
        ('TERMINATED', 'Terminated'),
    ]

    contract_number = models.CharField(max_length=50, unique=True, help_text="Official Defense Contract Identifier")
    title = models.CharField(max_length=255)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='contracts')
    tender = models.ForeignKey(TenderRFP, on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts')
    category = models.CharField(max_length=30, choices=DefenseItemCatalog.CATEGORY_CHOICES, default='AVIONICS')
    security_classification = models.CharField(max_length=20, choices=CLASSIFICATION_CHOICES, default='SECRET')
    
    total_contract_value = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    start_date = models.DateField()
    end_date = models.DateField()
    contract_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DRAFT')
    
    procurement_clause = models.CharField(max_length=100, default='Defense Acquisition Procedure (DAP) 2020')
    itar_controlled = models.BooleanField(default=True, help_text="ITAR / EAR export restriction controls apply")
    scope_of_contract = models.TextField()
    security_guidelines = models.TextField(blank=True, help_text="Facility security & clearance protocols")
    
    contracting_officer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='managed_contracts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.contract_number} - {self.title}"

    @property
    def total_disbursed(self):
        from invoicing.models import PaymentDisbursement
        payments = PaymentDisbursement.objects.filter(invoice__contract=self)
        total = sum(p.amount for p in payments)
        return total

    @property
    def completion_progress_pct(self):
        total_milestones = self.milestones.count()
        if total_milestones == 0:
            return 0
        completed = self.milestones.filter(status__in=['INSPECTION_PASSED', 'INVOICED', 'PAID']).count()
        return int((completed / total_milestones) * 100)


class ContractMilestone(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Initiation'),
        ('IN_PROGRESS', 'Under Production / Development'),
        ('DELIVERABLE_SUBMITTED', 'Deliverable Submitted by Contractor'),
        ('INSPECTION_PASSED', 'Military Inspection Passed (DD-250)'),
        ('INVOICED', 'Invoiced by Vendor'),
        ('PAID', 'Milestone Payment Settled'),
    ]

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='milestones')
    milestone_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    weightage_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)
    milestone_amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    completion_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['milestone_number']

    def __str__(self):
        return f"M{self.milestone_number}: {self.title} ({self.contract.contract_number})"


class ContractAmendment(models.Model):
    TYPE_CHOICES = [
        ('COST_REVISION', 'Financial Value Adjustment'),
        ('TIME_EXTENSION', 'Schedule / Timeline Extension'),
        ('SCOPE_CHANGE', 'Technical Scope Modification'),
        ('SPECIFICATION_UPGRADE', 'Avionics / Hardware Spec Upgrade'),
    ]

    STATUS_CHOICES = [
        ('PROPOSED', 'Proposed / Under Review'),
        ('APPROVED', 'Approved & Executed'),
        ('REJECTED', 'Rejected'),
    ]

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='amendments')
    amendment_number = models.CharField(max_length=30)
    amendment_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='TIME_EXTENSION')
    description = models.TextField()
    financial_impact = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, help_text="Amount added or subtracted")
    new_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PROPOSED')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.contract.contract_number} - {self.amendment_number} ({self.get_amendment_type_display()})"


class ContractLifecycleLog(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='lifecycle_logs')
    from_status = models.CharField(max_length=30)
    to_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.contract.contract_number}: {self.from_status} -> {self.to_status}"
