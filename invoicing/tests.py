from decimal import Decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from core.models import CustomUser
from vendors.models import Vendor
from contracts.models import Contract, ContractMilestone
from invoicing.models import InspectionCertificate, Invoice, PaymentDisbursement

class InvoicingAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.inspector = CustomUser.objects.create_user(
            username='dgqa_inspector',
            password='TestPassword@123',
            role='DEFENSE_INSPECTOR',
            security_clearance='SECRET'
        )
        self.finance_officer = CustomUser.objects.create_user(
            username='pcda_finance',
            password='TestPassword@123',
            role='FINANCE_OFFICER',
            security_clearance='SECRET'
        )
        self.vendor = Vendor.objects.create(
            name='Bharat Dynamics Limited (BDL)',
            vendor_code='VND-BDL-01',
            contact_person='P. Srinivas',
            email='contracts@bdl.in',
            phone='040-23456100'
        )
        self.contract = Contract.objects.create(
            contract_number='CTR-BDL-2026',
            title='Torpedo Propulsion Delivery',
            vendor=self.vendor,
            category='MISSILE_SYSTEMS',
            security_classification='TOP_SECRET',
            total_contract_value=Decimal('50000000.00'),
            start_date=date(2026, 1, 1),
            end_date=date(2027, 1, 1),
            contract_status='ACTIVE'
        )
        self.milestone = ContractMilestone.objects.create(
            contract=self.contract,
            milestone_number=1,
            title='Factory Acceptance Test',
            description='Range validation',
            due_date=date(2026, 6, 1),
            weightage_percentage=Decimal('100.00'),
            milestone_amount=Decimal('50000000.00'),
            status='DELIVERABLE_SUBMITTED'
        )

    def test_dd250_inspection_digital_signature_and_milestone_update(self):
        """Verify DD-250 inspection generates SHA-256 digital stamp and marks milestone passed."""
        cert = InspectionCertificate.objects.create(
            certificate_number='DD250-TEST-001',
            contract=self.contract,
            milestone=self.milestone,
            inspector=self.inspector,
            inspection_date=date(2026, 6, 2),
            inspection_location='DRDO Range Chandipur',
            status='PASSED',
            qa_report_number='DGQA-TR-2026',
            findings_and_notes='All mil-spec thermal and shock tolerances verified.'
        )

        # Check digital signature exists and has 64 hex characters (SHA-256)
        self.assertIsNotNone(cert.digital_signature)
        self.assertEqual(len(cert.digital_signature), 64)

        # Milestone status should automatically transition to INSPECTION_PASSED
        self.milestone.refresh_from_db()
        self.assertEqual(self.milestone.status, 'INSPECTION_PASSED')

    def test_invoice_retention_and_net_payable_calculation(self):
        """
        Verify DAP 2020 5% defense retention deduction:
        Gross Amount = 50,000,000
        Retention (5%) = 2,500,000
        Net Payable = 47,500,000
        """
        invoice = Invoice.objects.create(
            invoice_number='INV-TEST-001',
            contract=self.contract,
            milestone=self.milestone,
            vendor=self.vendor,
            invoice_date=date(2026, 6, 5),
            due_date=date(2026, 7, 5),
            gross_amount=Decimal('50000000.00'),
            tax_amount=Decimal('0.00'),
            withholding_retention_pct=Decimal('5.00')
        )

        self.assertEqual(invoice.withholding_amount, Decimal('2500000.00'))
        self.assertEqual(invoice.net_payable_amount, Decimal('47500000.00'))

    def test_three_way_match_and_treasury_disbursement(self):
        """Verify automated 3-Way Match validation and PCDA treasury settlement."""
        cert = InspectionCertificate.objects.create(
            certificate_number='DD250-TEST-002',
            contract=self.contract,
            milestone=self.milestone,
            inspector=self.inspector,
            inspection_date=date(2026, 6, 2),
            status='PASSED',
            findings_and_notes='Compliant.'
        )
        invoice = Invoice.objects.create(
            invoice_number='INV-TEST-002',
            contract=self.contract,
            milestone=self.milestone,
            vendor=self.vendor,
            inspection_cert=cert,
            invoice_date=date(2026, 6, 5),
            due_date=date(2026, 7, 5),
            gross_amount=Decimal('50000000.00'),
            payment_status='SUBMITTED'
        )

        self.client.login(username='pcda_finance', password='TestPassword@123')

        # Trigger 3-Way Match Verification
        verify_resp = self.client.post(
            reverse('invoice_verify_three_way', kwargs={'pk': invoice.pk}),
            {'action': 'VERIFY'}
        )
        self.assertEqual(verify_resp.status_code, 302)
        invoice.refresh_from_db()
        self.assertEqual(invoice.payment_status, 'THREE_WAY_MATCH_VERIFIED')

        # Approve by Finance Auditor
        approve_resp = self.client.post(
            reverse('invoice_verify_three_way', kwargs={'pk': invoice.pk}),
            {'action': 'AUDIT_APPROVE'}
        )
        self.assertEqual(approve_resp.status_code, 302)
        invoice.refresh_from_db()
        self.assertEqual(invoice.payment_status, 'AUDIT_APPROVED')

        # Execute PCDA Treasury Disbursement via RTGS
        disb_resp = self.client.post(
            reverse('payment_disbursement_create', kwargs={'invoice_pk': invoice.pk}),
            {
                'disbursement_reference': 'DEF-RTGS-991283',
                'disbursement_date': date(2026, 6, 10),
                'amount': invoice.net_payable_amount,
                'payment_method': 'SBI_GOV_RTGS',
                'bank_reference': 'SBIN0029381283',
                'remarks': 'Sanction order PCDA/2026/089 cleared.'
            }
        )
        self.assertEqual(disb_resp.status_code, 302)

        invoice.refresh_from_db()
        self.milestone.refresh_from_db()
        self.assertEqual(invoice.payment_status, 'PAID')
        self.assertEqual(self.milestone.status, 'PAID')
