from django.test import TestCase, Client
from django.urls import reverse
from core.models import CustomUser, AuditLog

class CoreAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='officer_rajesh',
            password='TestPassword@123',
            role='PROCUREMENT_OFFICER',
            security_clearance='SECRET',
            department='Air Headquarters Procurement Directorate',
            service_id='IAF-9921'
        )

    def test_custom_user_creation(self):
        """Verify CustomUser fields and role-based clearance attributes."""
        self.assertEqual(self.user.username, 'officer_rajesh')
        self.assertEqual(self.user.role, 'PROCUREMENT_OFFICER')
        self.assertEqual(self.user.security_clearance, 'SECRET')
        self.assertEqual(self.user.service_id, 'IAF-9921')
        self.assertTrue(self.user.check_password('TestPassword@123'))
        self.assertIn('Procurement Officer', str(self.user))

    def test_audit_log_creation(self):
        """Verify defense tamper-evident audit logging."""
        log = AuditLog.objects.create(
            user=self.user,
            action='CONTRACT_APPROVED',
            module='CONTRACTS',
            target_id='CTR-2026-001',
            target_repr='Tejas Radar Contract',
            details='Approved under DAP 2020 Make-in-India provisions.',
            ip_address='10.0.0.1'
        )
        self.assertEqual(log.action, 'CONTRACT_APPROVED')
        self.assertEqual(log.target_id, 'CTR-2026-001')
        self.assertIn('CONTRACT_APPROVED', str(log))
        self.assertIn('CONTRACTS', str(log))

    def test_unauthenticated_dashboard_redirect(self):
        """Unauthenticated access to defense command center should redirect to login."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_authenticated_dashboard_access(self):
        """Authenticated officer should successfully access defense command center."""
        self.client.login(username='officer_rajesh', password='TestPassword@123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Defense Command Center')
