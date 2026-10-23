from django.contrib import admin
from .models import DefenseItemCatalog, ProcurementRequisition, RequisitionItem, TenderRFP, TenderBid

@admin.register(DefenseItemCatalog)
class DefenseItemCatalogAdmin(admin.ModelAdmin):
    list_display = ('item_code', 'name', 'category', 'unit_of_measure', 'estimated_unit_price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('item_code', 'name', 'specifications')

class RequisitionItemInline(admin.TabularInline):
    model = RequisitionItem
    extra = 1

@admin.register(ProcurementRequisition)
class ProcurementRequisitionAdmin(admin.ModelAdmin):
    list_display = ('requisition_number', 'title', 'category', 'demanding_service', 'priority', 'estimated_total_cost', 'status', 'required_by_date')
    list_filter = ('category', 'priority', 'status', 'demanding_service')
    search_fields = ('requisition_number', 'title', 'justification')
    inlines = [RequisitionItemInline]

class TenderBidInline(admin.TabularInline):
    model = TenderBid
    extra = 0

@admin.register(TenderRFP)
class TenderRFPAdmin(admin.ModelAdmin):
    list_display = ('tender_number', 'title', 'tender_type', 'security_clearance_required', 'estimated_value', 'submission_deadline', 'status')
    list_filter = ('tender_type', 'security_clearance_required', 'status')
    search_fields = ('tender_number', 'title', 'scope_of_work')
    inlines = [TenderBidInline]

@admin.register(TenderBid)
class TenderBidAdmin(admin.ModelAdmin):
    list_display = ('tender', 'vendor', 'bid_amount', 'delivery_timeline_months', 'technical_compliance', 'bid_status')
    list_filter = ('bid_status', 'technical_compliance')
    search_fields = ('tender__tender_number', 'vendor__name')
