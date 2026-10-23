from django.db import models
from django.conf import settings

class Vendor(models.Model):
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

    CLEARANCE_CHOICES = [
        ('UNCLASSIFIED', 'Unclassified'),
        ('CONFIDENTIAL', 'Confidential'),
        ('SECRET', 'Secret'),
        ('TOP_SECRET', 'Top Secret (TS/SCI)'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active / Cleared'),
        ('PENDING_VERIFICATION', 'Pending Security Review'),
        ('PROBATION', 'Under Watch / Probation'),
        ('SUSPENDED', 'Suspended'),
        ('BLACKLISTED', 'Blacklisted (Debarred)'),
    ]

    TIER_CHOICES = [
        ('TIER_1_PRIME', 'Tier 1 - Prime Defense Contractor'),
        ('TIER_2_MAJOR_SUB', 'Tier 2 - Major Subsystem Integrator'),
        ('TIER_3_COMPONENT', 'Tier 3 - Specialized Component Supplier'),
    ]

    name = models.CharField(max_length=200)
    vendor_code = models.CharField(max_length=50, unique=True, help_text="Unique Defense Vendor Code")
    cage_code = models.CharField(max_length=20, blank=True, help_text="CAGE / NCAGE Code")
    duns_number = models.CharField(max_length=20, blank=True, help_text="D-U-N-S Number")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='AVIONICS')
    security_clearance = models.CharField(max_length=20, choices=CLEARANCE_CHOICES, default='SECRET')
    clearance_expiry = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ACTIVE')
    tier = models.CharField(max_length=30, choices=TIER_CHOICES, default='TIER_1_PRIME')
    
    contact_person = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.TextField(blank=True)
    country = models.CharField(max_length=80, default='India')
    
    certifications = models.CharField(max_length=255, default='AS9100D, ISO 9001:2015, ISO 27001')
    itar_compliant = models.BooleanField(default=True, help_text="ITAR / Export Control Compliant")
    performance_rating = models.DecimalField(max_digits=5, decimal_places=2, default=85.00, help_text="Score out of 100")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.vendor_code} - {self.name} ({self.get_tier_display()})"


class VendorEvaluation(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    evaluation_date = models.DateField()
    
    technical_score = models.DecimalField(max_digits=5, decimal_places=2, default=80.0, help_text="Max 100 (Weight: 25%)")
    delivery_score = models.DecimalField(max_digits=5, decimal_places=2, default=80.0, help_text="Max 100 (Weight: 20%)")
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, default=80.0, help_text="Max 100 (Weight: 25%)")
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2, default=85.0, help_text="Max 100 (Weight: 15%)")
    cost_score = models.DecimalField(max_digits=5, decimal_places=2, default=80.0, help_text="Max 100 (Weight: 15%)")
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, default=80.0)
    
    strengths = models.TextField(blank=True)
    risk_assessment = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_score(self):
        weighted = (
            float(self.technical_score) * 0.25 +
            float(self.delivery_score) * 0.20 +
            float(self.quality_score) * 0.25 +
            float(self.compliance_score) * 0.15 +
            float(self.cost_score) * 0.15
        )
        self.overall_score = round(weighted, 2)
        return self.overall_score

    def save(self, *args, **kwargs):
        self.calculate_score()
        super().save(*args, **kwargs)
        # Update vendor's overall performance rating
        avg_score = self.vendor.evaluations.aggregate(models.Avg('overall_score'))['overall_score__avg']
        if avg_score is not None:
            self.vendor.performance_rating = round(avg_score, 2)
            self.vendor.save(update_fields=['performance_rating'])

    def __str__(self):
        return f"Evaluation of {self.vendor.name} on {self.evaluation_date} - Score: {self.overall_score}"
