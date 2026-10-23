from django.db import models
from django.conf import settings
from vendors.models import Vendor

class DefenseItemCatalog(models.Model):
    CATEGORY_CHOICES = [
        ('AEROSPACE', 'Aerospace & Airframes'),
        ('AVIONICS', 'Avionics & Flight Control'),
        ('RADAR_EW', 'Radar, Sonar & Electronic Warfare'),
        ('MISSILE_SYSTEMS', 'Missiles & Precision Munitions'),
        ('ARMORED_VEHICLES', 'Armored Tactical Vehicles'),
        ('NAVAL', 'Naval & Subsurface Systems'),
        ('CYBER_DEFENSE', 'Tactical Cyber & C4ISR'),
        ('MUNITIONS', 'Ammunition & Ordnance'),
        ('LOGISTICS', 'Strategic Logistics & MRO'),
    ]

    item_code = models.CharField(max_length=60, unique=True, help_text="NATO Stock No. (NSN) or Mil-Spec Code")
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='AVIONICS')
    unit_of_measure = models.CharField(max_length=30, default='Unit')
    estimated_unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=100000.00)
    specifications = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.item_code}] {self.name}"


class ProcurementRequisition(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Routine'),
        ('MEDIUM', 'Priority Operational'),
        ('HIGH', 'Urgent Defense Requirement'),
        ('CRITICAL_OPERATIONAL', 'Critical / War-Reserve Requirement'),
    ]

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted for Directorate Review'),
        ('APPROVED', 'Approved by Contracting Authority'),
        ('TENDER_ISSUED', 'RFP / Tender Issued'),
        ('FULFILLED', 'Procured & Fulfilled'),
        ('REJECTED', 'Rejected'),
    ]

    requisition_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=DefenseItemCatalog.CATEGORY_CHOICES, default='AVIONICS')
    demanding_service = models.CharField(max_length=120, default='Air Force Command HQ', help_text="Service Branch or Command Unit")
    priority = models.CharField(max_length=30, choices=PRIORITY_CHOICES, default='HIGH')
    justification = models.TextField(help_text="Operational / Strategic Defense Justification")
    estimated_total_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    required_by_date = models.DateField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DRAFT')
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='requisitions_created')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='requisitions_approved')
    approval_date = models.DateField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.requisition_number} - {self.title} ({self.get_status_display()})"


class RequisitionItem(models.Model):
    requisition = models.ForeignKey(ProcurementRequisition, on_delete=models.CASCADE, related_name='items')
    catalog_item = models.ForeignKey(DefenseItemCatalog, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.description}"


class TenderRFP(models.Model):
    TENDER_TYPE_CHOICES = [
        ('OPEN_COMPETITIVE', 'Open Global / National Competitive Bid'),
        ('LIMITED_TENDER', 'Limited Defense Qualified Tender'),
        ('SINGLE_SOURCE_GOV_NOMINATED', 'Nominated Single-Source / Strategic Strategic Partner'),
    ]

    CLEARANCE_CHOICES = [
        ('UNCLASSIFIED', 'Unclassified'),
        ('CONFIDENTIAL', 'Confidential'),
        ('SECRET', 'Secret'),
        ('TOP_SECRET', 'Top Secret (TS/SCI)'),
    ]

    STATUS_CHOICES = [
        ('DRAFT', 'Draft Notice'),
        ('PUBLISHED', 'Published (Accepting Bids)'),
        ('TECHNICAL_EVALUATION', 'Technical Evaluation in Progress'),
        ('COMMERCIAL_EVALUATION', 'Commercial / L1 Evaluation'),
        ('AWARDED', 'Awarded to Prime Contractor'),
        ('CANCELLED', 'Cancelled / Retendered'),
    ]

    tender_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    requisition = models.ForeignKey(ProcurementRequisition, on_delete=models.SET_NULL, null=True, blank=True, related_name='tenders')
    tender_type = models.CharField(max_length=40, choices=TENDER_TYPE_CHOICES, default='LIMITED_TENDER')
    security_clearance_required = models.CharField(max_length=20, choices=CLEARANCE_CHOICES, default='SECRET')
    estimated_value = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    publication_date = models.DateField()
    submission_deadline = models.DateField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PUBLISHED')
    scope_of_work = models.TextField()
    terms_and_conditions = models.TextField(blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-publication_date']

    def __str__(self):
        return f"{self.tender_number} - {self.title}"


class TenderBid(models.Model):
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('UNDER_EVALUATION', 'Under Evaluation'),
        ('SHORTLISTED', 'Technically Qualified'),
        ('ACCEPTED_L1', 'Selected (Lowest Compliant L1 Bid)'),
        ('REJECTED', 'Disqualified / Rejected'),
    ]

    tender = models.ForeignKey(TenderRFP, on_delete=models.CASCADE, related_name='bids')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='bids')
    bid_amount = models.DecimalField(max_digits=14, decimal_places=2)
    delivery_timeline_months = models.PositiveIntegerField(default=12)
    technical_compliance = models.BooleanField(default=True)
    bid_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='SUBMITTED')
    evaluation_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid by {self.vendor.name} for {self.tender.tender_number} ({self.bid_amount})"
