from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from core.models import CustomUser
from vendors.models import Vendor
from contracts.models import Contract, ContractMilestone, ContractAmendment, ContractLifecycleLog

class ContractAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.officer = CustomUser.objects.create_user(
            username='col_malhotra',
            password='TestPassword@123',
            role='CONTRACTING_OFFICER',
            security_clearance='TOP_SECRET'
        )
        self.vendor = Vendor.objects.create(
            name='Hindustan Aeronautics Limited (HAL)',
            vendor_code='VND-HAL-01',
            contact_person='S. Kulkarni',
            email='hal@hal.co.in',
            phone='080-22320101'
        )
        self.contract = Contract.objects.create(
            contract_number='CTR-TEST-0042',
            title='Tejas Fighter Jet Airframe Integration',
            vendor=self.vendor,
            category='AEROSPACE',
            security_classification='TOP_SECRET',
            total_contract_value=Decimal('100000000.00'),
            currency='INR',
            start_date=date(2026, 1, 1),
            end_date=date(2027, 12, 31),
            contract_status='ACTIVE',
            procurement_clause='DAP 2020 Strategic Partnership',
            itar_controlled=True,
            scope_of_contract='Assembly of 16 Tejas Mk-1A airframes',
            contracting_officer=self.officer
        )

    def test_contract_milestones_and_completion_progress(self):
        """Verify completion progress percentage calculation based on milestone statuses."""
        m1 = ContractMilestone.objects.create(
            contract=self.contract,
            milestone_number=1,
            title='Preliminary Design Review',
            description='Design baseline',
            due_date=date(2026, 4, 1),
            weightage_percentage=Decimal('50.00'),
            milestone_amount=Decimal('50000000.00'),
            status='INSPECTION_PASSED'
        )
        m2 = ContractMilestone.objects.create(
            contract=self.contract,
            milestone_number=2,
            title='Flight Line Delivery',
            description='Physical delivery',
            due_date=date(2027, 4, 1),
            weightage_percentage=Decimal('50.00'),
            milestone_amount=Decimal('50000000.00'),
            status='IN_PROGRESS'
        )

        # 1 out of 2 completed (INSPECTION_PASSED) = 50%
        self.assertEqual(self.contract.completion_progress_pct, 50)

    def test_contract_amendment_financial_and_date_adjustment(self):
        """Verify contract amendment adjusts total contract value and extends completion date."""
        self.client.login(username='col_malhotra', password='TestPassword@123')
        new_date = date(2028, 6, 30)
        cost_increase = Decimal('5000000.00')

        response = self.client.post(
            reverse('contract_amendment_create', kwargs={'contract_pk': self.contract.pk}),
            {
                'amendment_number': 'AMD-01',
                'amendment_type': 'COST_REVISION',
                'description': 'Additional avionics integration sanctioned by Air HQ.',
                'financial_impact': cost_increase,
                'new_end_date': new_date,
                'status': 'APPROVED'
            }
        )
        self.assertEqual(response.status_code, 302)

        self.contract.refresh_from_db()
        self.assertEqual(self.contract.contract_status, 'AMENDED')
        self.assertEqual(self.contract.total_contract_value, Decimal('105000000.00'))
        self.assertEqual(self.contract.end_date, new_date)

    def test_contract_lifecycle_transition(self):
        """Verify state machine transition and lifecycle log generation."""
        self.client.login(username='col_malhotra', password='TestPassword@123')
        response = self.client.post(
            reverse('contract_change_status', kwargs={'pk': self.contract.pk}),
            {
                'new_status': 'COMPLETED',
                'notes': 'All deliveries received and final acceptance signed.'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.contract_status, 'COMPLETED')

        # Verify lifecycle log created
        log = ContractLifecycleLog.objects.filter(contract=self.contract, to_status='COMPLETED').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.from_status, 'ACTIVE')
