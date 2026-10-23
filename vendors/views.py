import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q

from .models import Vendor, VendorEvaluation
from .forms import VendorForm, VendorEvaluationForm
from core.models import AuditLog

@login_required
def vendor_list(request):
    vendors = Vendor.objects.all()
    q = request.GET.get('q')
    category = request.GET.get('category')
    clearance = request.GET.get('clearance')
    tier = request.GET.get('tier')
    status = request.GET.get('status')

    if q:
        vendors = vendors.filter(
            Q(name__icontains=q) |
            Q(vendor_code__icontains=q) |
            Q(cage_code__icontains=q) |
            Q(contact_person__icontains=q)
        )
    if category:
        vendors = vendors.filter(category=category)
    if clearance:
        vendors = vendors.filter(security_clearance=clearance)
    if tier:
        vendors = vendors.filter(tier=tier)
    if status:
        vendors = vendors.filter(status=status)

    return render(request, 'vendors/vendor_list.html', {
        'vendors': vendors,
        'categories': Vendor.CATEGORY_CHOICES,
        'clearances': Vendor.CLEARANCE_CHOICES,
        'tiers': Vendor.TIER_CHOICES,
        'statuses': Vendor.STATUS_CHOICES,
        'search_query': q or '',
        'selected_category': category or '',
        'selected_clearance': clearance or '',
        'selected_tier': tier or '',
        'selected_status': status or '',
    })

@login_required
def vendor_detail(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    evaluations = vendor.evaluations.all().order_by('-evaluation_date')
    contracts = vendor.contracts.all().order_by('-created_at')
    invoices = vendor.invoices.all().order_by('-created_at')

    return render(request, 'vendors/vendor_detail.html', {
        'vendor': vendor,
        'evaluations': evaluations,
        'contracts': contracts,
        'invoices': invoices,
    })

@login_required
def vendor_create(request):
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            vendor = form.save()
            AuditLog.objects.create(
                user=request.user,
                action='CREATE_VENDOR',
                module='VENDORS',
                target_id=vendor.vendor_code,
                target_repr=vendor.name,
                details=f"Registered defense contractor {vendor.name} (CAGE: {vendor.cage_code}) with {vendor.get_security_clearance_display()} clearance.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Defense contractor '{vendor.name}' registered successfully.")
            return redirect('vendor_detail', pk=vendor.pk)
    else:
        form = VendorForm()
    return render(request, 'vendors/vendor_form.html', {'form': form, 'title': 'Register Defense Contractor / Vendor'})

@login_required
def vendor_edit(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            vendor = form.save()
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE_VENDOR',
                module='VENDORS',
                target_id=vendor.vendor_code,
                target_repr=vendor.name,
                details=f"Updated defense profile for {vendor.name}.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Vendor details for '{vendor.name}' updated.")
            return redirect('vendor_detail', pk=vendor.pk)
    else:
        form = VendorForm(instance=vendor)
    return render(request, 'vendors/vendor_form.html', {'form': form, 'title': f'Edit Vendor: {vendor.name}', 'vendor': vendor})

@login_required
def vendor_evaluation_create(request, vendor_pk):
    vendor = get_object_or_404(Vendor, pk=vendor_pk)
    if request.method == 'POST':
        form = VendorEvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.vendor = vendor
            evaluation.evaluator = request.user
            evaluation.save()

            AuditLog.objects.create(
                user=request.user,
                action='EVALUATE_VENDOR',
                module='VENDORS',
                target_id=vendor.vendor_code,
                target_repr=vendor.name,
                details=f"Conducted multi-criteria performance audit. Overall score: {evaluation.overall_score}/100.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Performance Evaluation submitted! Weighted score: {evaluation.overall_score}/100. Vendor rating updated.")
            return redirect('vendor_detail', pk=vendor.pk)
    else:
        form = VendorEvaluationForm()
    return render(request, 'vendors/evaluation_form.html', {'form': form, 'vendor': vendor})

@login_required
def export_vendors_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="defense_contractors_registry.csv"'
    writer = csv.writer(response)
    writer.writerow(['Vendor Code', 'Name', 'CAGE Code', 'DUNS', 'Category', 'Clearance Level', 'Tier', 'Status', 'Performance Score', 'ITAR Compliant', 'Contact', 'Email'])

    for v in Vendor.objects.all():
        writer.writerow([
            v.vendor_code, v.name, v.cage_code, v.duns_number, v.get_category_display(),
            v.get_security_clearance_display(), v.get_tier_display(), v.get_status_display(),
            v.performance_rating, 'YES' if v.itar_compliant else 'NO', v.contact_person, v.email
        ])
    return response
