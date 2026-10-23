from django import forms
from .models import ProcurementRequisition, RequisitionItem, TenderRFP, TenderBid, DefenseItemCatalog

class ProcurementRequisitionForm(forms.ModelForm):
    class Meta:
        model = ProcurementRequisition
        fields = ['requisition_number', 'title', 'category', 'demanding_service', 'priority', 'justification', 'estimated_total_cost', 'required_by_date']
        widgets = {
            'requisition_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. REQ-2026-IAF-009'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descriptive title of operational procurement'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'demanding_service': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Air HQ / Western Naval Command'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'justification': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Defense rationale, operational threat matrix, strategic stock replenishment...'}),
            'estimated_total_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000', 'placeholder': 'Estimated INR'}),
            'required_by_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class RequisitionItemForm(forms.ModelForm):
    class Meta:
        model = RequisitionItem
        fields = ['catalog_item', 'description', 'quantity', 'unit_price']
        widgets = {
            'catalog_item': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Detailed item nomenclature'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '100'}),
        }


class TenderRFPForm(forms.ModelForm):
    class Meta:
        model = TenderRFP
        fields = [
            'tender_number', 'title', 'requisition', 'tender_type',
            'security_clearance_required', 'estimated_value',
            'publication_date', 'submission_deadline', 'scope_of_work', 'terms_and_conditions'
        ]
        widgets = {
            'tender_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. RFP-MOD-2026-0044'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Official Tender / RFP Notice Header'}),
            'requisition': forms.Select(attrs={'class': 'form-select'}),
            'tender_type': forms.Select(attrs={'class': 'form-select'}),
            'security_clearance_required': forms.Select(attrs={'class': 'form-select'}),
            'estimated_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'submission_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'scope_of_work': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Mil-spec parameters, environmental testing standards, trials schedule...'}),
            'terms_and_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Make-in-India DAP clauses, warranty, liquidated damages penalty...'}),
        }


class TenderBidForm(forms.ModelForm):
    class Meta:
        model = TenderBid
        fields = ['vendor', 'bid_amount', 'delivery_timeline_months', 'technical_compliance', 'evaluation_notes']
        widgets = {
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'bid_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000', 'placeholder': 'Commercial Bid in INR'}),
            'delivery_timeline_months': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'technical_compliance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'evaluation_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Bid remarks and compliance deviations if any...'}),
        }


class DefenseCatalogForm(forms.ModelForm):
    class Meta:
        model = DefenseItemCatalog
        fields = ['item_code', 'name', 'category', 'unit_of_measure', 'estimated_unit_price', 'specifications', 'is_active']
        widgets = {
            'item_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. NSN-5840-01-9921'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Defense item nomenclature'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'unit_of_measure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Set, System, Unit'}),
            'estimated_unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '100'}),
            'specifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
