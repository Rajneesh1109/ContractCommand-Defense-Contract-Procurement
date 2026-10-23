from django.contrib import admin
from .models import InspectionCertificate, Invoice, PaymentDisbursement

class PaymentDisbursementInline(admin.TabularInline):
    model = PaymentDisbursement
    extra = 0
    fields = ('disbursement_reference', 'disbursement_date', 'amount', 'payment_method', 'bank_reference')

@admin.register(InspectionCertificate)
class InspectionCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'contract', 'milestone', 'inspector', 'inspection_date', 'status')
    list_filter = ('status', 'inspection_date')
    search_fields = ('certificate_number', 'contract__contract_number', 'findings_and_notes', 'qa_report_number')
    readonly_fields = ('digital_signature', 'created_at')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'contract', 'vendor', 'invoice_date', 'gross_amount', 'net_payable_amount', 'payment_status')
    list_filter = ('payment_status', 'invoice_date')
    search_fields = ('invoice_number', 'contract__contract_number', 'vendor__name')
    inlines = [PaymentDisbursementInline]
    readonly_fields = ('withholding_amount', 'net_payable_amount', 'created_at', 'updated_at')

@admin.register(PaymentDisbursement)
class PaymentDisbursementAdmin(admin.ModelAdmin):
    list_display = ('disbursement_reference', 'invoice', 'disbursement_date', 'amount', 'payment_method', 'disbursed_by')
    list_filter = ('payment_method', 'disbursement_date')
    search_fields = ('disbursement_reference', 'bank_reference', 'invoice__invoice_number')
