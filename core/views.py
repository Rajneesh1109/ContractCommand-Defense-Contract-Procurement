import csv
import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Count, Avg
from decimal import Decimal

from .models import CustomUser, AuditLog
from .forms import LoginForm, UserProfileForm
from contracts.models import Contract, ContractMilestone
from vendors.models import Vendor
from procurement.models import ProcurementRequisition, TenderRFP
from invoicing.models import Invoice, InspectionCertificate, PaymentDisbursement

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            AuditLog.objects.create(
                user=user,
                action='LOGIN_SUCCESS',
                module='SECURITY',
                details=f"User {user.username} authenticated with {user.get_security_clearance_display()} clearance.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Welcome, {user.get_full_name() or user.username} [{user.get_role_display()}]. Clearance verified.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid Service ID or password.")
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated:
        AuditLog.objects.create(
            user=request.user,
            action='LOGOUT',
            module='SECURITY',
            details=f"User {request.user.username} signed out.",
            ip_address=request.META.get('REMOTE_ADDR')
        )
    logout(request)
    messages.info(request, "You have been securely logged out.")
    return redirect('login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile details updated successfully.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'core/profile.html', {'form': form})

@login_required
def dashboard(request):
    contracts_qs = Contract.objects.all()
    total_contract_value = contracts_qs.aggregate(Sum('total_contract_value'))['total_contract_value__sum'] or Decimal('0.00')
    active_contracts = contracts_qs.filter(contract_status__in=['ACTIVE', 'AMENDED']).count()
    total_contracts = contracts_qs.count()
    
    # Financials
    total_disbursed = PaymentDisbursement.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Vendors
    total_vendors = Vendor.objects.count()
    avg_vendor_rating = Vendor.objects.aggregate(Avg('performance_rating'))['performance_rating__avg'] or 85.0
    
    # Procurement & Requisitions
    total_requisitions = ProcurementRequisition.objects.count()
    active_tenders = TenderRFP.objects.filter(status__in=['PUBLISHED', 'TECHNICAL_EVALUATION', 'COMMERCIAL_EVALUATION']).count()
    
    # Invoicing & Inspections
    pending_inspections = ContractMilestone.objects.filter(status='DELIVERABLE_SUBMITTED').count()
    pending_invoices = Invoice.objects.filter(payment_status__in=['SUBMITTED', 'THREE_WAY_MATCH_VERIFIED']).count()
    
    # Chart Data: Category Breakdown
    category_data = Contract.objects.values('category').annotate(total_val=Sum('total_contract_value')).order_by('-total_val')
    category_labels = [dict(Contract._meta.get_field('category').choices).get(c['category'], c['category']) for c in category_data]
    category_values = [float(c['total_val'] or 0) / 10000000.0 for c in category_data] # In Crores
    
    # Chart Data: Lifecycle Pipeline
    status_data = Contract.objects.values('contract_status').annotate(count=Count('id')).order_by('contract_status')
    status_labels = [dict(Contract.STATUS_CHOICES).get(s['contract_status'], s['contract_status']) for s in status_data]
    status_counts = [s['count'] for s in status_data]

    # Chart Data: Milestones health
    milestone_stats = ContractMilestone.objects.values('status').annotate(count=Count('id'))
    ms_labels = [dict(ContractMilestone.STATUS_CHOICES).get(m['status'], m['status']) for m in milestone_stats]
    ms_counts = [m['count'] for m in milestone_stats]

    # Recent items
    recent_contracts = contracts_qs.order_by('-created_at')[:5]
    recent_audit_logs = AuditLog.objects.order_by('-timestamp')[:8]
    upcoming_milestones = ContractMilestone.objects.filter(status__in=['PENDING', 'IN_PROGRESS', 'DELIVERABLE_SUBMITTED']).order_by('due_date')[:5]

    context = {
        'total_contract_value': total_contract_value,
        'active_contracts': active_contracts,
        'total_contracts': total_contracts,
        'total_disbursed': total_disbursed,
        'disbursed_pct': int((float(total_disbursed) / float(total_contract_value) * 100)) if total_contract_value > 0 else 0,
        'total_vendors': total_vendors,
        'avg_vendor_rating': round(avg_vendor_rating, 1),
        'total_requisitions': total_requisitions,
        'active_tenders': active_tenders,
        'pending_inspections': pending_inspections,
        'pending_invoices': pending_invoices,
        'category_labels_json': json.dumps(category_labels),
        'category_values_json': json.dumps(category_values),
        'status_labels_json': json.dumps(status_labels),
        'status_counts_json': json.dumps(status_counts),
        'ms_labels_json': json.dumps(ms_labels),
        'ms_counts_json': json.dumps(ms_counts),
        'recent_contracts': recent_contracts,
        'recent_audit_logs': recent_audit_logs,
        'upcoming_milestones': upcoming_milestones,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def audit_logs_view(request):
    logs = AuditLog.objects.all().select_related('user')
    module_filter = request.GET.get('module')
    action_filter = request.GET.get('action')
    search = request.GET.get('q')

    if module_filter:
        logs = logs.filter(module=module_filter)
    if action_filter:
        logs = logs.filter(action__icontains=action_filter)
    if search:
        logs = logs.filter(details__icontains=search) | logs.filter(target_id__icontains=search)

    modules = AuditLog.objects.values_list('module', flat=True).distinct()
    return render(request, 'core/audit_logs.html', {
        'logs': logs[:200],
        'modules': modules,
        'selected_module': module_filter,
        'search_query': search or '',
    })

@login_required
def export_audit_logs_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="defense_audit_trail.csv"'
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'User', 'Role', 'Module', 'Action', 'Target ID', 'Target Name', 'IP Address', 'Details'])

    logs = AuditLog.objects.all().select_related('user')[:500]
    for log in logs:
        writer.writerow([
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.user.username if log.user else 'System',
            log.user.get_role_display() if log.user else 'N/A',
            log.module,
            log.action,
            log.target_id,
            log.target_repr,
            log.ip_address,
            log.details,
        ])
    return response
