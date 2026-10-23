import os
import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contractcommand.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import AuditLog
from vendors.models import Vendor, VendorEvaluation
from procurement.models import DefenseItemCatalog, ProcurementRequisition, RequisitionItem, TenderRFP, TenderBid
from contracts.models import Contract, ContractMilestone, ContractAmendment, ContractLifecycleLog
from invoicing.models import InspectionCertificate, Invoice, PaymentDisbursement

User = get_user_model()

def run():
    print("Populating ContractCommand Defense Database with realistic mock data...")

    # 1. Create Users
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@defenseprocure.gov.in',
            'first_name': 'Chief Admin',
            'last_name': 'Directorate',
            'role': 'ADMIN',
            'service_id': 'DEF-HQ-001',
            'security_clearance': 'TOP_SECRET',
            'department': 'Ministry of Defense Acquisition Secretariat',
            'is_superuser': True,
            'is_staff': True,
        },
        {
            'username': 'rajesh_sharma',
            'email': 'wgcdr.rajesh@iaf.gov.in',
            'first_name': 'Rajesh',
            'last_name': 'Sharma',
            'role': 'PROCUREMENT_OFFICER',
            'service_id': 'IAF-88219-F',
            'security_clearance': 'SECRET',
            'department': 'Air Headquarters Directorate of Procurement',
            'is_staff': True,
        },
        {
            'username': 'vikram_malhotra',
            'email': 'col.vikram@army.gov.in',
            'first_name': 'Vikram',
            'last_name': 'Malhotra',
            'role': 'CONTRACTING_OFFICER',
            'service_id': 'IC-64102-M',
            'security_clearance': 'TOP_SECRET',
            'department': 'Central Contract Management Directorate',
            'is_staff': True,
        },
        {
            'username': 'sunita_rao',
            'email': 'dr.sunita@drdo.gov.in',
            'first_name': 'Sunita',
            'last_name': 'Rao',
            'role': 'DEFENSE_INSPECTOR',
            'service_id': 'DRDO-QA-441',
            'security_clearance': 'SECRET',
            'department': 'Directorate General of Quality Assurance (DGQA)',
            'is_staff': True,
        },
        {
            'username': 'ajay_mehra',
            'email': 'ajay.mehra@defencedad.gov.in',
            'first_name': 'Ajay',
            'last_name': 'Mehra',
            'role': 'FINANCE_OFFICER',
            'service_id': 'DAD-FIN-9912',
            'security_clearance': 'SECRET',
            'department': 'Principal Controller of Defense Accounts (PCDA)',
            'is_staff': True,
        },
        {
            'username': 'amitabh_sen',
            'email': 'majgen.sen@mod.gov.in',
            'first_name': 'Amitabh',
            'last_name': 'Sen',
            'role': 'AUDITOR',
            'service_id': 'AUD-GEN-07',
            'security_clearance': 'TOP_SECRET',
            'department': 'Defense Audit & Oversight Commission',
            'is_staff': True,
        },
        {
            'username': 'hal_rep',
            'email': 'contracts@hal-india.co.in',
            'first_name': 'Sunil',
            'last_name': 'Kulkarni',
            'role': 'VENDOR_REP',
            'service_id': 'HAL-EXEC-901',
            'security_clearance': 'SECRET',
            'department': 'Hindustan Aeronautics Ltd (HAL) Defense Division',
            'is_staff': False,
        }
    ]

    created_users = {}
    for u in users_data:
        user, created = User.objects.get_or_create(username=u['username'], defaults=u)
        user.set_password('Admin@1234')
        user.save()
        created_users[u['username']] = user
        if created:
            print(f"Created user: {user.username} ({user.get_role_display()})")

    admin_user = created_users['admin']
    proc_officer = created_users['rajesh_sharma']
    cont_officer = created_users['vikram_malhotra']
    inspector = created_users['sunita_rao']
    fin_officer = created_users['ajay_mehra']

    # 2. Defense Vendors
    vendors_data = [
        {
            'name': 'Hindustan Aeronautics Limited (HAL)',
            'vendor_code': 'VND-HAL-01',
            'cage_code': 'CAGE-HAL01',
            'duns_number': '650123891',
            'category': 'AEROSPACE',
            'security_clearance': 'TOP_SECRET',
            'clearance_expiry': date(2028, 12, 31),
            'status': 'ACTIVE',
            'tier': 'TIER_1_PRIME',
            'contact_person': 'Sunil Kulkarni (GM Contracts)',
            'email': 'contracts@hal-india.co.in',
            'phone': '+91-80-22320101',
            'address': '15/1 Cubbon Road, P.B. No. 5150, Bengaluru, Karnataka 560001',
            'country': 'India',
            'certifications': 'AS9100D, ISO 9001:2015, DGAQA Approved',
            'itar_compliant': True,
            'performance_rating': Decimal('94.50'),
        },
        {
            'name': 'Bharat Electronics Limited (BEL)',
            'vendor_code': 'VND-BEL-02',
            'cage_code': 'CAGE-BEL88',
            'duns_number': '650987112',
            'category': 'RADAR_EW',
            'security_clearance': 'TOP_SECRET',
            'clearance_expiry': date(2028, 6, 30),
            'status': 'ACTIVE',
            'tier': 'TIER_1_PRIME',
            'contact_person': 'R. K. Verma (Director Defense Radars)',
            'email': 'defense.contracts@bel.co.in',
            'phone': '+91-80-25039300',
            'address': 'Outer Ring Road, Nagavara, Bengaluru 560045',
            'country': 'India',
            'certifications': 'AS9100D, ISO 27001, CMMI Level 5',
            'itar_compliant': True,
            'performance_rating': Decimal('92.80'),
        },
        {
            'name': 'Tata Advanced Systems Limited (TASL)',
            'vendor_code': 'VND-TASL-03',
            'cage_code': 'CAGE-TASL5',
            'duns_number': '652300441',
            'category': 'AEROSPACE',
            'security_clearance': 'SECRET',
            'clearance_expiry': date(2027, 9, 30),
            'status': 'ACTIVE',
            'tier': 'TIER_1_PRIME',
            'contact_person': 'Ananya Deshmukh (VP Strategic Procurements)',
            'email': 'procurement@tataadvanced.com',
            'phone': '+91-40-66993000',
            'address': 'Hardware Park, Shamshabad, Hyderabad 501218',
            'country': 'India',
            'certifications': 'AS9100D, ISO 9001, NADCAP Certified',
            'itar_compliant': True,
            'performance_rating': Decimal('89.20'),
        },
        {
            'name': 'Bharat Dynamics Limited (BDL)',
            'vendor_code': 'VND-BDL-04',
            'cage_code': 'CAGE-BDL19',
            'duns_number': '651102987',
            'category': 'MISSILE_SYSTEMS',
            'security_clearance': 'TOP_SECRET',
            'clearance_expiry': date(2029, 3, 31),
            'status': 'ACTIVE',
            'tier': 'TIER_1_PRIME',
            'contact_person': 'Col P. Srinivas (Retd, Head Marketing)',
            'email': 'contracts@bdl-india.in',
            'phone': '+91-40-23456100',
            'address': 'Kanchanbagh, Hyderabad, Telangana 500058',
            'country': 'India',
            'certifications': 'ISO 9001:2015, Mil-Std 810G Certified',
            'itar_compliant': True,
            'performance_rating': Decimal('91.00'),
        },
        {
            'name': 'Larsen & Toubro Defense',
            'vendor_code': 'VND-LNT-05',
            'cage_code': 'CAGE-LNT90',
            'duns_number': '650456123',
            'category': 'NAVAL',
            'security_clearance': 'TOP_SECRET',
            'clearance_expiry': date(2028, 1, 15),
            'status': 'ACTIVE',
            'tier': 'TIER_1_PRIME',
            'contact_person': 'Capt S. Nair (IN Retd, VP Submarines)',
            'email': 'naval.defense@larsentoubro.com',
            'phone': '+91-22-67525656',
            'address': 'L&T House, Ballard Estate, Mumbai 400001',
            'country': 'India',
            'certifications': 'AS9100D, ISO 45001, MoD Industrial License',
            'itar_compliant': True,
            'performance_rating': Decimal('95.10'),
        },
        {
            'name': 'Zen Technologies Tactical Simulators',
            'vendor_code': 'VND-ZEN-06',
            'cage_code': 'CAGE-ZEN33',
            'duns_number': '653998124',
            'category': 'CYBER_DEFENSE',
            'security_clearance': 'CONFIDENTIAL',
            'clearance_expiry': date(2026, 11, 20),
            'status': 'ACTIVE',
            'tier': 'TIER_2_MAJOR_SUB',
            'contact_person': 'Mohit Chawla (Head Defense Solutions)',
            'email': 'simulations@zentechnologies.com',
            'phone': '+91-40-27813281',
            'address': 'B-42, Electronic Complex, Kushaiguda, Hyderabad 500062',
            'country': 'India',
            'certifications': 'ISO 9001, ISO 27001',
            'itar_compliant': True,
            'performance_rating': Decimal('84.00'),
        }
    ]

    created_vendors = {}
    for v_data in vendors_data:
        v, created = Vendor.objects.get_or_create(vendor_code=v_data['vendor_code'], defaults=v_data)
        created_vendors[v_data['vendor_code']] = v

    # Vendor Evaluations
    eval1, _ = VendorEvaluation.objects.get_or_create(
        vendor=created_vendors['VND-HAL-01'],
        evaluation_date=date(2026, 1, 15),
        defaults={
            'evaluator': cont_officer,
            'technical_score': Decimal('96.0'),
            'delivery_score': Decimal('90.0'),
            'quality_score': Decimal('97.0'),
            'compliance_score': Decimal('98.0'),
            'cost_score': Decimal('88.0'),
            'strengths': 'Proven indigenous supersonic airframe manufacturing, exceptional flight test infrastructure.',
            'risk_assessment': 'Long lead times on imported third-party composite components.',
            'recommendations': 'Continue prime contractor tier for Light Combat Aircraft variants.',
        }
    )

    eval2, _ = VendorEvaluation.objects.get_or_create(
        vendor=created_vendors['VND-BEL-02'],
        evaluation_date=date(2026, 2, 10),
        defaults={
            'evaluator': cont_officer,
            'technical_score': Decimal('95.0'),
            'delivery_score': Decimal('92.0'),
            'quality_score': Decimal('94.0'),
            'compliance_score': Decimal('95.0'),
            'cost_score': Decimal('89.0'),
            'strengths': 'State-of-the-art Gallium Nitride (GaN) radar TR modules and EW jammers.',
            'risk_assessment': 'High capacity utilization; order pipeline requires phased delivery.',
            'recommendations': 'Prime tier cleared for airborne and naval radar tenders.',
        }
    )

    # 3. Defense Item Catalog
    catalog_items_data = [
        {
            'item_code': 'NSN-1560-LCA-9021',
            'name': 'Digital Flight Control Computer (DFCC) Mk-1A',
            'category': 'AVIONICS',
            'unit_of_measure': 'Unit',
            'estimated_unit_price': Decimal('3500000.00'),
            'specifications': 'Quadruplex fly-by-wire redundant architecture, Mil-Std 1553B / 1760 bus compliant.',
        },
        {
            'item_code': 'NSN-5840-RDR-7714',
            'name': 'Active Electronically Scanned Array (AESA) T/R Module Set',
            'category': 'RADAR_EW',
            'unit_of_measure': 'Set',
            'estimated_unit_price': Decimal('7500000.00'),
            'specifications': 'X-Band GaN high-power transmit/receive elements, multi-target tracking > 120km.',
        },
        {
            'item_code': 'NSN-5820-SDR-5501',
            'name': 'Software Defined Radio (SDR) Tactical Airborne Transceiver',
            'category': 'CYBER_DEFENSE',
            'unit_of_measure': 'System',
            'estimated_unit_price': Decimal('1800000.00'),
            'specifications': 'V/UHF, ECCM frequency-hopping, integrated Type-1 military encryption.',
        },
        {
            'item_code': 'NSN-1420-MSL-3309',
            'name': 'Millimeter-Wave RF Active Seeker Unit',
            'category': 'MISSILE_SYSTEMS',
            'unit_of_measure': 'Unit',
            'estimated_unit_price': Decimal('5200000.00'),
            'specifications': 'Ka-band terminal homing seeker, jam-resistant digital processing, anti-armor/air.',
        },
        {
            'item_code': 'NSN-1550-UAV-6102',
            'name': 'Autonomous Swarm Reconnaissance UAV Airframe & Electro-Optics',
            'category': 'AEROSPACE',
            'unit_of_measure': 'System',
            'estimated_unit_price': Decimal('2400000.00'),
            'specifications': 'Carbon-fiber composite stealth airframe, FLIR day/night thermal payload, mesh networking.',
        },
        {
            'item_code': 'NSN-2010-NAV-1188',
            'name': 'Integrated Combat Management Console (CMS-26)',
            'category': 'NAVAL',
            'unit_of_measure': 'System',
            'estimated_unit_price': Decimal('9800000.00'),
            'specifications': 'Ruggedized naval console, fiber-optic redundant ring, multi-sensor radar/sonar fusion.',
        }
    ]

    catalog_dict = {}
    for ci in catalog_items_data:
        c_obj, _ = DefenseItemCatalog.objects.get_or_create(item_code=ci['item_code'], defaults=ci)
        catalog_dict[ci['item_code']] = c_obj

    # 4. Procurement Requisitions
    req1, _ = ProcurementRequisition.objects.get_or_create(
        requisition_number='REQ-2026-IAF-001',
        defaults={
            'title': 'Procurement of Uttam AESA Radar Modules for 48 Tejas Mk-1A Squadrons',
            'category': 'RADAR_EW',
            'demanding_service': 'Air Force Command HQ (Vayu Bhawan)',
            'priority': 'CRITICAL_OPERATIONAL',
            'justification': 'Replacement of legacy mechanically steered radars with indigenous GaN AESA modules to achieve air superiority and electronic counter-countermeasures.',
            'estimated_total_cost': Decimal('185000000.00'),
            'required_by_date': date(2026, 11, 30),
            'status': 'TENDER_ISSUED',
            'created_by': proc_officer,
            'approved_by': cont_officer,
            'approval_date': date(2026, 1, 10),
            'approval_notes': 'Cleared by Defense Acquisition Council (DAC). Essential operational priority.',
        }
    )
    RequisitionItem.objects.get_or_create(
        requisition=req1,
        catalog_item=catalog_dict['NSN-5840-RDR-7714'],
        defaults={'description': 'GaN AESA Radar T/R Module Sets', 'quantity': 20, 'unit_price': Decimal('7500000.00')}
    )
    RequisitionItem.objects.get_or_create(
        requisition=req1,
        catalog_item=catalog_dict['NSN-1560-LCA-9021'],
        defaults={'description': 'Digital Flight Control Computer Interfacing Units', 'quantity': 10, 'unit_price': Decimal('3500000.00')}
    )

    req2, _ = ProcurementRequisition.objects.get_or_create(
        requisition_number='REQ-2026-ARM-002',
        defaults={
            'title': 'High-Altitude Autonomous Swarm Reconnaissance Systems for Border Surveillance',
            'category': 'AEROSPACE',
            'demanding_service': 'Northern Army Command HQ (Udhampur)',
            'priority': 'HIGH',
            'justification': 'Real-time 24x7 all-weather intelligence, surveillance, and target acquisition (ISTAR) over disputed high-altitude ridgelines.',
            'estimated_total_cost': Decimal('120000000.00'),
            'required_by_date': date(2027, 2, 28),
            'status': 'APPROVED',
            'created_by': proc_officer,
            'approved_by': cont_officer,
            'approval_date': date(2026, 2, 1),
            'approval_notes': 'Fast-track emergency procurement authorization invoked.',
        }
    )
    RequisitionItem.objects.get_or_create(
        requisition=req2,
        catalog_item=catalog_dict['NSN-1550-UAV-6102'],
        defaults={'description': 'Autonomous Swarm Reconnaissance Units with Thermal FLIR', 'quantity': 50, 'unit_price': Decimal('2400000.00')}
    )

    req3, _ = ProcurementRequisition.objects.get_or_create(
        requisition_number='REQ-2026-NAV-003',
        defaults={
            'title': 'Next-Generation Naval Combat Management Consoles (Project 17B Frigates)',
            'category': 'NAVAL',
            'demanding_service': 'Western Naval Command (Mumbai Dockyard)',
            'priority': 'MEDIUM',
            'justification': 'Modernization of surface fleet warfare centers with MIL-SPEC CMS-26 multi-sensor consoles.',
            'estimated_total_cost': Decimal('98000000.00'),
            'required_by_date': date(2027, 6, 30),
            'status': 'SUBMITTED',
            'created_by': proc_officer,
        }
    )

    # 5. Tenders / RFPs
    tender1, _ = TenderRFP.objects.get_or_create(
        tender_number='RFP-MOD-2026-0018',
        defaults={
            'title': 'Production and System Integration of Airborne AESA Radar Modules (Tejas Mk-1A)',
            'requisition': req1,
            'tender_type': 'LIMITED_TENDER',
            'security_clearance_required': 'SECRET',
            'estimated_value': Decimal('185000000.00'),
            'publication_date': date(2026, 1, 15),
            'submission_deadline': date(2026, 2, 28),
            'status': 'AWARDED',
            'scope_of_work': 'Manufacturing, calibration, environmental stress screening (ESS), and flight test qualification of AESA transmitter/receiver sets conforming to Mil-Std-810G and Mil-Std-461E.',
            'terms_and_conditions': 'Delivery schedule within 24 months. Bank Guarantee of 5% contract value required. DAP 2020 Make-in-India minimum 60% indigenous content.',
            'created_by': cont_officer,
        }
    )

    bid1, _ = TenderBid.objects.get_or_create(
        tender=tender1,
        vendor=created_vendors['VND-BEL-02'],
        defaults={
            'bid_amount': Decimal('182000000.00'),
            'delivery_timeline_months': 22,
            'technical_compliance': True,
            'bid_status': 'ACCEPTED_L1',
            'evaluation_notes': 'Compliant with all technical parameters. Full indigenous GaN fabrication capability demonstrated at BEL Bangalore.',
        }
    )

    bid2, _ = TenderBid.objects.get_or_create(
        tender=tender1,
        vendor=created_vendors['VND-TASL-03'],
        defaults={
            'bid_amount': Decimal('188500000.00'),
            'delivery_timeline_months': 24,
            'technical_compliance': True,
            'bid_status': 'SHORTLISTED',
            'evaluation_notes': 'Technically qualified; higher price than L1.',
        }
    )

    tender2, _ = TenderRFP.objects.get_or_create(
        tender_number='RFP-MOD-2026-0027',
        defaults={
            'title': 'Tactical High-Bandwidth Airborne SDR Encryption Sets',
            'requisition': None,
            'tender_type': 'OPEN_COMPETITIVE',
            'security_clearance_required': 'SECRET',
            'estimated_value': Decimal('72000000.00'),
            'publication_date': date(2026, 2, 5),
            'submission_deadline': date(2026, 3, 25),
            'status': 'PUBLISHED',
            'scope_of_work': 'Supply of tactical secure radio equipment for tri-services secure tactical datalink integration.',
            'created_by': cont_officer,
        }
    )

    # 6. Defense Contracts
    ctr1, _ = Contract.objects.get_or_create(
        contract_number='CTR-DEF-2026-0042',
        defaults={
            'title': 'Procurement & Series Integration of Uttam AESA Radar Modules for Fighter Jets',
            'vendor': created_vendors['VND-BEL-02'],
            'tender': tender1,
            'category': 'RADAR_EW',
            'security_classification': 'SECRET',
            'total_contract_value': Decimal('182000000.00'),
            'currency': 'INR',
            'start_date': date(2026, 3, 1),
            'end_date': date(2027, 12, 31),
            'contract_status': 'ACTIVE',
            'procurement_clause': 'Defense Acquisition Procedure (DAP) 2020 - Buy (Indian-IDDM)',
            'itar_controlled': True,
            'scope_of_contract': 'Full series manufacture, hardware-in-loop (HIL) testing, environmental qualification, and delivery of 20 shipsets of AESA Transmit/Receive Modules with spares and field support.',
            'security_guidelines': 'Personnel handling schematics must hold valid SECRET clearance. Encrypted air-gapped data transfers mandatory.',
            'contracting_officer': cont_officer,
        }
    )

    ctr2, _ = Contract.objects.get_or_create(
        contract_number='CTR-DEF-2025-0108',
        defaults={
            'title': 'Light Combat Aircraft Tejas Mk-1A Airframe Fabrication & Sub-Assembly',
            'vendor': created_vendors['VND-HAL-01'],
            'tender': None,
            'category': 'AEROSPACE',
            'security_classification': 'TOP_SECRET',
            'total_contract_value': Decimal('345000000.00'),
            'currency': 'INR',
            'start_date': date(2025, 4, 1),
            'end_date': date(2027, 3, 31),
            'contract_status': 'ACTIVE',
            'procurement_clause': 'DAP 2020 Strategic Partnership Model',
            'itar_controlled': True,
            'scope_of_contract': 'Assembly of fuselage, wing structures, cockpit integration, and hydraulic testing for 16 LCA airframes.',
            'contracting_officer': cont_officer,
        }
    )

    ctr3, _ = Contract.objects.get_or_create(
        contract_number='CTR-DEF-2026-0091',
        defaults={
            'title': 'Underwater Heavyweight Torpedo Propulsion & Guidance Subsystems',
            'vendor': created_vendors['VND-BDL-04'],
            'tender': None,
            'category': 'MISSILE_SYSTEMS',
            'security_classification': 'TOP_SECRET',
            'total_contract_value': Decimal('95000000.00'),
            'currency': 'INR',
            'start_date': date(2026, 2, 15),
            'end_date': date(2027, 8, 31),
            'contract_status': 'LEGAL_TECH_REVIEW',
            'procurement_clause': 'DAP 2020 Buy (Global - Manufacture in India)',
            'itar_controlled': True,
            'scope_of_contract': 'Supply of battery propulsion modules and acoustic homing wire-guided torpedo guidance heads.',
            'contracting_officer': cont_officer,
        }
    )

    # 7. Milestones for Contract CTR-DEF-2026-0042
    m1, _ = ContractMilestone.objects.get_or_create(
        contract=ctr1,
        milestone_number=1,
        defaults={
            'title': 'Critical Design Review (CDR) & Prototype GaN Module Bench Acceptance',
            'description': 'Submission and defense approval of technical design data package, simulation models, and lab qualification test reports.',
            'due_date': date(2026, 4, 30),
            'weightage_percentage': Decimal('20.00'),
            'milestone_amount': Decimal('36400000.00'),
            'status': 'PAID',
            'completion_date': date(2026, 4, 25),
        }
    )

    m2, _ = ContractMilestone.objects.get_or_create(
        contract=ctr1,
        milestone_number=2,
        defaults={
            'title': 'Factory Acceptance Test (FAT) & Thermal Vacuum Chamber Environmental Qualification',
            'description': 'Rigorous testing of first batch of 5 AESA antenna sets under -40C to +70C vibration, EMI/EMC MIL-STD-461E screening.',
            'due_date': date(2026, 8, 30),
            'weightage_percentage': Decimal('30.00'),
            'milestone_amount': Decimal('54600000.00'),
            'status': 'INSPECTION_PASSED',
            'completion_date': date(2026, 8, 20),
        }
    )

    m3, _ = ContractMilestone.objects.get_or_create(
        contract=ctr1,
        milestone_number=3,
        defaults={
            'title': 'Flight Line Integration & Air-to-Air Radar Range Trials on Tejas Flying Test Bed',
            'description': 'Flight clearance certification and radar tracking verification against aerial targets at Chandipur ITR.',
            'due_date': date(2026, 12, 15),
            'weightage_percentage': Decimal('30.00'),
            'milestone_amount': Decimal('54600000.00'),
            'status': 'IN_PROGRESS',
        }
    )

    m4, _ = ContractMilestone.objects.get_or_create(
        contract=ctr1,
        milestone_number=4,
        defaults={
            'title': 'Full Series Delivery of 20 Radar Shipsets, Maintenance Spares & IETM Manuals',
            'description': 'Complete physical delivery at Air Force Depots with Interactive Electronic Technical Manuals and 2-year warranty support.',
            'due_date': date(2027, 11, 30),
            'weightage_percentage': Decimal('20.00'),
            'milestone_amount': Decimal('36400000.00'),
            'status': 'PENDING',
        }
    )

    # 8. Contract Amendment for CTR-DEF-2026-0042
    amd1, _ = ContractAmendment.objects.get_or_create(
        contract=ctr1,
        amendment_number='AMD-01',
        defaults={
            'amendment_type': 'SPECIFICATION_UPGRADE',
            'description': 'Enhanced ECCM (Electronic Counter-Countermeasures) frequency hopping rate upgrade to support next-gen EW pods.',
            'financial_impact': Decimal('2500000.00'),
            'new_end_date': date(2027, 12, 31),
            'status': 'APPROVED',
            'approved_by': cont_officer,
        }
    )

    # 9. Inspection Certificates (DD-250 equivalent)
    cert1, _ = InspectionCertificate.objects.get_or_create(
        certificate_number='DD250-2026-0034',
        defaults={
            'contract': ctr1,
            'milestone': m1,
            'inspector': inspector,
            'inspection_date': date(2026, 4, 25),
            'inspection_location': 'DGQA Radar Testing Complex, BEL Bengaluru',
            'status': 'PASSED',
            'qa_report_number': 'QA-TR-2026-781',
            'findings_and_notes': 'All 1553B bus messages validated. MTBF simulation verified > 3000 operational hours. 100% compliant with Mil-Spec tolerances.',
        }
    )

    cert2, _ = InspectionCertificate.objects.get_or_create(
        certificate_number='DD250-2026-0082',
        defaults={
            'contract': ctr1,
            'milestone': m2,
            'inspector': inspector,
            'inspection_date': date(2026, 8, 20),
            'inspection_location': 'Environmental Test Facility, ASTE Air Force Station Yelahanka',
            'status': 'PASSED',
            'qa_report_number': 'DGQA-FAT-2026-119',
            'findings_and_notes': 'Thermal shock, vibration and EMI/EMC compliance tests passed with distinction. Five AESA T/R sets cleared for flight trials.',
        }
    )

    # 10. Invoices
    inv1, _ = Invoice.objects.get_or_create(
        invoice_number='INV-BEL-2026-011',
        defaults={
            'contract': ctr1,
            'milestone': m1,
            'vendor': created_vendors['VND-BEL-02'],
            'inspection_cert': cert1,
            'invoice_date': date(2026, 4, 28),
            'due_date': date(2026, 5, 28),
            'gross_amount': Decimal('36400000.00'),
            'tax_amount': Decimal('0.00'), # Defense procurement GST exemption certificate applied
            'withholding_retention_pct': Decimal('5.00'),
            'payment_status': 'PAID',
            'notes': 'Milestone 1 (CDR) claim against DD-250 Cert # DD250-2026-0034.',
        }
    )

    inv2, _ = Invoice.objects.get_or_create(
        invoice_number='INV-BEL-2026-048',
        defaults={
            'contract': ctr1,
            'milestone': m2,
            'vendor': created_vendors['VND-BEL-02'],
            'inspection_cert': cert2,
            'invoice_date': date(2026, 8, 22),
            'due_date': date(2026, 9, 22),
            'gross_amount': Decimal('54600000.00'),
            'tax_amount': Decimal('0.00'),
            'withholding_retention_pct': Decimal('5.00'),
            'payment_status': 'THREE_WAY_MATCH_VERIFIED',
            'notes': 'Milestone 2 (FAT) claim submitted with approved DD-250 inspection sheet. Verified by 3-Way Match algorithm.',
        }
    )

    # 11. Payment Disbursement for Invoice 1
    disb1, _ = PaymentDisbursement.objects.get_or_create(
        disbursement_reference='DEF-PCDA-RTGS-2026-89412',
        defaults={
            'invoice': inv1,
            'disbursement_date': date(2026, 5, 12),
            'amount': inv1.net_payable_amount,
            'payment_method': 'SBI_GOV_RTGS',
            'bank_reference': 'SBINR52026051288910023',
            'disbursed_by': fin_officer,
            'remarks': 'Principal Controller of Defense Accounts electronic treasury transfer executed into BEL designated defense escrow account.',
        }
    )

    # 12. Audit Logs
    AuditLog.objects.get_or_create(
        action='CONTRACT_APPROVED',
        module='CONTRACTS',
        target_id=ctr1.contract_number,
        defaults={
            'user': cont_officer,
            'target_repr': str(ctr1),
            'details': f"Contract {ctr1.contract_number} formally signed and approved for execution with {ctr1.vendor.name}.",
            'ip_address': '10.14.88.22',
        }
    )

    AuditLog.objects.get_or_create(
        action='INSPECTION_SIGNED',
        module='INSPECTIONS',
        target_id=cert2.certificate_number,
        defaults={
            'user': inspector,
            'target_repr': str(cert2),
            'details': f"DD-250 Inspection certificate digitally stamped for Milestone 2 with QA Report {cert2.qa_report_number}.",
            'ip_address': '10.14.92.10',
        }
    )

    AuditLog.objects.get_or_create(
        action='PAYMENT_PROCESSED',
        module='INVOICING',
        target_id=disb1.disbursement_reference,
        defaults={
            'user': fin_officer,
            'target_repr': str(disb1),
            'details': f"Defense Treasury RTGS payment of ₹{disb1.amount} cleared for Invoice {inv1.invoice_number}.",
            'ip_address': '10.14.77.104',
        }
    )

    print("Populate data finished successfully! All realistic defense entities created.")

if __name__ == '__main__':
    run()
