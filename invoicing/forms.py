from django import forms
from .models import InspectionCertificate, Invoice, PaymentDisbursement

class InspectionCertificateForm(forms.ModelForm):
    class Meta:
        model = InspectionCertificate
        fields = [
            'certificate_number', 'contract', 'milestone', 'inspection_date',
            'inspection_location', 'status', 'qa_report_number', 'findings_and_notes'
        ]
        widgets = {
            'certificate_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. DD250-2026-0091'}),
            'contract': forms.Select(attrs={'class': 'form-select'}),
            'milestone': forms.Select(attrs={'class': 'form-select'}),
            'inspection_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'inspection_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Testing range, bench lab or air base'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'qa_report_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'QA/FAT Lab Report Ref'}),
            'findings_and_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Test parameters verified, tolerance checks, calibration certificates checked...'}),
        }


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'contract', 'milestone', 'vendor', 'inspection_cert',
            'invoice_date', 'due_date', 'gross_amount', 'tax_amount',
            'withholding_retention_pct', 'notes'
        ]
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. INV-DEF-2026-0072'}),
            'contract': forms.Select(attrs={'class': 'form-select'}),
            'milestone': forms.Select(attrs={'class': 'form-select'}),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'inspection_cert': forms.Select(attrs={'class': 'form-select'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gross_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '100'}),
            'withholding_retention_pct': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'value': '5.0'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Claim remarks, bank account details for defense escrow...'}),
        }


class PaymentDisbursementForm(forms.ModelForm):
    class Meta:
        model = PaymentDisbursement
        fields = ['disbursement_reference', 'disbursement_date', 'amount', 'payment_method', 'bank_reference', 'remarks']
        widgets = {
            'disbursement_reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. DEF-PCDA-RTGS-98231'}),
            'disbursement_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'bank_reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RBI UTR / Treasury Ref'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Payment sanction orders and auditor clearance notes...'}),
        }
