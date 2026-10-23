from django import forms
from .models import Contract, ContractMilestone, ContractAmendment

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'contract_number', 'title', 'vendor', 'tender', 'category',
            'security_classification', 'total_contract_value', 'currency',
            'start_date', 'end_date', 'contract_status', 'procurement_clause',
            'itar_controlled', 'scope_of_contract', 'security_guidelines', 'contracting_officer'
        ]
        widgets = {
            'contract_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CTR-DEF-2026-0042'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contract Title / Scope Heading'}),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'tender': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'security_classification': forms.Select(attrs={'class': 'form-select'}),
            'total_contract_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'INR / USD'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contract_status': forms.Select(attrs={'class': 'form-select'}),
            'procurement_clause': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DAP 2020 / FAR / DFARS'}),
            'itar_controlled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'scope_of_contract': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'security_guidelines': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Clearance, air-gap, storage specifications...'}),
            'contracting_officer': forms.Select(attrs={'class': 'form-select'}),
        }


class ContractMilestoneForm(forms.ModelForm):
    class Meta:
        model = ContractMilestone
        fields = ['milestone_number', 'title', 'description', 'due_date', 'weightage_percentage', 'milestone_amount', 'status']
        widgets = {
            'milestone_number': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Factory Acceptance Test (FAT)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'weightage_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Percentage %'}),
            'milestone_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000', 'placeholder': 'INR Milestone Value'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class ContractAmendmentForm(forms.ModelForm):
    class Meta:
        model = ContractAmendment
        fields = ['amendment_number', 'amendment_type', 'description', 'financial_impact', 'new_end_date', 'status']
        widgets = {
            'amendment_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. AMD-02'}),
            'amendment_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Justification and military committee minutes approval...'}),
            'financial_impact': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000', 'placeholder': 'Amount added or subtracted'}),
            'new_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
