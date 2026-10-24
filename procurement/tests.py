from decimal import Decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from core.models import CustomUser
from vendors.models import Vendor
from procurement.models import DefenseItemCatalog, ProcurementRequisition, RequisitionItem, TenderRFP, TenderBid

class ProcurementAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.officer = CustomUser.objects.create_user(
            username='proc_officer',
            password='TestPassword@123',
            role='PROCUREMENT_OFFICER',
            security_clearance='SECRET'
        )
        self.contracting_officer = CustomUser.objects.create_user(
            username='approving_col',
            password='TestPassword@123',
            role='CONTRACTING_OFFICER',
            security_clearance='TOP_SECRET'
        )
        self.catalog_item = DefenseItemCatalog.objects.create(
            item_code='NSN-5840-RDR-001',
            name='AESA Radar Transceiver Module',
            category='RADAR_EW',
            unit_of_measure='Set',
            estimated_unit_price=Decimal('5000000.00'),
            specifications='X-Band GaN elements'
        )
        self.vendor_l1 = Vendor.objects.create(
            name='Tata Advanced Systems Limited (TASL)',
            vendor_code='VND-TASL-01',
            contact_person='A. Deshmukh',
            email='tasl@tata.com',
            phone='9999999999'
        )
        self.vendor_l2 = Vendor.objects.create(
            name='Kalyani Strategic Systems',
            vendor_code='VND-KAL-02',
            contact_person='B. Kalyani',
            email='kalyani@defense.com',
            phone='8888888888'
        )

    def test_requisition_and_line_item_calculation(self):
        """Verify requisition total price auto-computation from line items."""
        req = ProcurementRequisition.objects.create(
            requisition_number='REQ-TEST-001',
            title='Procurement of AESA Radar Transceiver Modules',
            category='RADAR_EW',
            demanding_service='Air HQ',
            priority='HIGH',
            justification='Tejas Mk-1A radar modernization',
            required_by_date=date(2026, 12, 31),
            created_by=self.officer
        )
        item = RequisitionItem.objects.create(
            requisition=req,
            catalog_item=self.catalog_item,
            description='GaN Radar TR Module Set',
            quantity=4,
            unit_price=Decimal('5000000.00')
        )
        # Total price should be 4 * 5,000,000 = 20,000,000
        self.assertEqual(item.total_price, Decimal('20000000.00'))

    def test_requisition_approval_workflow(self):
        """Verify approving officer transition from DRAFT to APPROVED."""
        self.client.login(username='approving_col', password='TestPassword@123')
        req = ProcurementRequisition.objects.create(
            requisition_number='REQ-TEST-002',
            title='Avionics Modernization',
            category='AVIONICS',
            demanding_service='Naval Aviation Command',
            priority='CRITICAL_OPERATIONAL',
            justification='Carrier-based fleet upgrade',
            required_by_date=date(2027, 1, 1),
            created_by=self.officer,
            status='SUBMITTED'
        )

        response = self.client.post(reverse('requisition_approve', kwargs={'pk': req.pk}), {
            'action': 'APPROVE',
            'approval_notes': 'Cleared by Defense Acquisition Council (DAC).'
        })
        self.assertEqual(response.status_code, 302)
        req.refresh_from_db()
        self.assertEqual(req.status, 'APPROVED')
        self.assertEqual(req.approved_by, self.contracting_officer)

    def test_tender_bidding_and_l1_award(self):
        """Verify commercial bidding and lowest-cost compliant L1 contractor selection."""
        self.client.login(username='approving_col', password='TestPassword@123')
        tender = TenderRFP.objects.create(
            tender_number='RFP-TEST-001',
            title='Radar Subsystem Procurement',
            tender_type='LIMITED_TENDER',
            security_clearance_required='SECRET',
            estimated_value=Decimal('50000000.00'),
            publication_date=date(2026, 1, 1),
            submission_deadline=date(2026, 3, 1),
            scope_of_work='AESA integration',
            created_by=self.contracting_officer,
            status='PUBLISHED'
        )

        bid_l1 = TenderBid.objects.create(
            tender=tender,
            vendor=self.vendor_l1,
            bid_amount=Decimal('45000000.00'),
            delivery_timeline_months=12,
            technical_compliance=True,
            bid_status='SUBMITTED'
        )
        bid_l2 = TenderBid.objects.create(
            tender=tender,
            vendor=self.vendor_l2,
            bid_amount=Decimal('48000000.00'),
            delivery_timeline_months=14,
            technical_compliance=True,
            bid_status='SUBMITTED'
        )

        # Award tender to L1 bidder
        response = self.client.post(reverse('tender_award', kwargs={'pk': tender.pk, 'bid_pk': bid_l1.pk}))
        self.assertEqual(response.status_code, 302)

        tender.refresh_from_db()
        bid_l1.refresh_from_db()
        bid_l2.refresh_from_db()

        self.assertEqual(tender.status, 'AWARDED')
        self.assertEqual(bid_l1.bid_status, 'ACCEPTED_L1')
        self.assertEqual(bid_l2.bid_status, 'REJECTED')
