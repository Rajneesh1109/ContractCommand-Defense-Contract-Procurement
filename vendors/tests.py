from decimal import Decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from core.models import CustomUser
from vendors.models import Vendor, VendorEvaluation

class VendorAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.auditor = CustomUser.objects.create_user(
            username='auditor_sen',
            password='TestPassword@123',
            role='AUDITOR',
            security_clearance='TOP_SECRET'
        )
        self.vendor = Vendor.objects.create(
            name='Bharat Electronics Limited (BEL)',
            vendor_code='VND-BEL-99',
            cage_code='CAGE-BEL99',
            duns_number='650987112',
            category='RADAR_EW',
            security_clearance='TOP_SECRET',
            tier='TIER_1_PRIME',
            contact_person='Dr. Verma',
            email='contracts@bel.co.in',
            phone='+91-80-25039300',
            itar_compliant=True,
            performance_rating=Decimal('85.00')
        )

    def test_vendor_creation(self):
        """Verify defense vendor attributes and tier status."""
        self.assertEqual(self.vendor.vendor_code, 'VND-BEL-99')
        self.assertEqual(self.vendor.cage_code, 'CAGE-BEL99')
        self.assertTrue(self.vendor.itar_compliant)
        self.assertIn('Prime Defense Contractor', str(self.vendor))

    def test_vendor_evaluation_score_calculation(self):
        """
        Verify the 5-factor weighted scorecard formula:
        (Tech*0.25) + (Delivery*0.20) + (Quality*0.25) + (Compliance*0.15) + (Cost*0.15)
        Expected: (90*0.25) + (80*0.20) + (100*0.25) + (90*0.15) + (80*0.15)
        = 22.5 + 16.0 + 25.0 + 13.5 + 12.0 = 89.0
        """
        evaluation = VendorEvaluation.objects.create(
            vendor=self.vendor,
            evaluator=self.auditor,
            evaluation_date=date(2026, 3, 1),
            technical_score=Decimal('90.0'),
            delivery_score=Decimal('80.0'),
            quality_score=Decimal('100.0'),
            compliance_score=Decimal('90.0'),
            cost_score=Decimal('80.0'),
            strengths='World-class AESA GaN radar modules and secure EW systems.',
        )

        expected_score = Decimal('89.00')
        self.assertEqual(evaluation.overall_score, expected_score)

        # Refresh vendor from DB and verify overall performance rating updated
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.performance_rating, expected_score)

    def test_vendor_list_and_detail_views(self):
        """Verify authenticated views for defense vendor directory."""
        self.client.login(username='auditor_sen', password='TestPassword@123')
        list_resp = self.client.get(reverse('vendor_list'))
        self.assertEqual(list_resp.status_code, 200)
        self.assertContains(list_resp, 'Bharat Electronics Limited')

        detail_resp = self.client.get(reverse('vendor_detail', kwargs={'pk': self.vendor.pk}))
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, 'CAGE-BEL99')
