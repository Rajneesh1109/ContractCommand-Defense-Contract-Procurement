from django import forms
from .models import Vendor, VendorEvaluation

class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            'name', 'vendor_code', 'cage_code', 'duns_number', 'category',
            'security_clearance', 'clearance_expiry', 'status', 'tier',
            'contact_person', 'email', 'phone', 'address', 'country',
            'certifications', 'itar_compliant', 'performance_rating'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bharat Dynamics Limited'}),
            'vendor_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. VND-BDL-04'}),
            'cage_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CAGE-1940A'}),
            'duns_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 651102987'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'security_clearance': forms.Select(attrs={'class': 'form-select'}),
            'clearance_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'tier': forms.Select(attrs={'class': 'form-select'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'certifications': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. AS9100D, ISO 9001:2015'}),
            'itar_compliant': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'performance_rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '100'}),
        }


class VendorEvaluationForm(forms.ModelForm):
    class Meta:
        model = VendorEvaluation
        fields = [
            'evaluation_date', 'technical_score', 'delivery_score', 'quality_score',
            'compliance_score', 'cost_score', 'strengths', 'risk_assessment', 'recommendations'
        ]
        widgets = {
            'evaluation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'technical_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0', 'max': '100', 'placeholder': 'Weight: 25%'}),
            'delivery_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0', 'max': '100', 'placeholder': 'Weight: 20%'}),
            'quality_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0', 'max': '100', 'placeholder': 'Weight: 25%'}),
            'compliance_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0', 'max': '100', 'placeholder': 'Weight: 15%'}),
            'cost_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0', 'max': '100', 'placeholder': 'Weight: 15%'}),
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Technical strengths, manufacturing capabilities, testing rig readiness...'}),
            'risk_assessment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Supply chain bottlenecks, obsolescence risk, single-source dependency...'}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tier clearance, corrective action requests, auditing intervals...'}),
        }
