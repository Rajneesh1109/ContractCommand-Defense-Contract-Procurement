from django.contrib import admin
from .models import Vendor, VendorEvaluation

class VendorEvaluationInline(admin.TabularInline):
    model = VendorEvaluation
    extra = 0
    fields = ('evaluation_date', 'technical_score', 'delivery_score', 'quality_score', 'compliance_score', 'cost_score', 'overall_score')
    readonly_fields = ('overall_score',)

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendor_code', 'name', 'category', 'tier', 'security_clearance', 'performance_rating', 'status')
    list_filter = ('category', 'tier', 'security_clearance', 'status', 'itar_compliant')
    search_fields = ('name', 'vendor_code', 'cage_code', 'duns_number', 'contact_person', 'email')
    inlines = [VendorEvaluationInline]

@admin.register(VendorEvaluation)
class VendorEvaluationAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'evaluation_date', 'evaluator', 'overall_score')
    list_filter = ('evaluation_date', 'overall_score')
    search_fields = ('vendor__name', 'vendor__vendor_code', 'strengths', 'recommendations')
