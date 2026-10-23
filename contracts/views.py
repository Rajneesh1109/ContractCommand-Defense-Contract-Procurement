import csv
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q, Sum

from .models import Contract, ContractMilestone, ContractAmendment, ContractLifecycleLog
from .forms import ContractForm, ContractMilestoneForm, ContractAmendmentForm
from core.models import AuditLog

@login_required
def contract_list(request):
    contracts = Contract.objects.all().select_related('vendor', 'contracting_officer')
    q = request.GET.get('q')
    category = request.GET.get('category')
    classification = request.GET.get('classification')
    status = request.GET.get('status')
    vendor_id = request.GET.get('vendor')

    if q:
        contracts = contracts.filter(
            Q(contract_number__icontains=q) |
            Q(title__icontains=q) |
            Q(vendor__name__icontains=q)
        )
    if category:
        contracts = contracts.filter(category=category)
    if classification:
        contracts = contracts.filter(security_classification=classification)
    if status:
        contracts = contracts.filter(contract_status=status)
    if vendor_id:
        contracts = contracts.filter(vendor_id=vendor_id)

    total_val = contracts.aggregate(Sum('total_contract_value'))['total_contract_value__sum'] or 0

    return render(request, 'contracts/contract_list.html', {
        'contracts': contracts,
        'categories': Contract._meta.get_field('category').choices,
        'classifications': Contract.CLASSIFICATION_CHOICES,
        'statuses': Contract.STATUS_CHOICES,
        'total_filtered_value': total_val,
        'search_query': q or '',
        'selected_category': category or '',
        'selected_classification': classification or '',
        'selected_status': status or '',
    })

@login_required
def contract_detail(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    milestones = contract.milestones.all().order_by('milestone_number')
    amendments = contract.amendments.all().order_by('-created_at')
    lifecycle_logs = contract.lifecycle_logs.all()
    invoices = contract.invoices.all().order_by('-invoice_date')
    inspection_certs = contract.inspection_certificates.all().order_by('-inspection_date')

    milestone_form = ContractMilestoneForm()
    amendment_form = ContractAmendmentForm()

    return render(request, 'contracts/contract_detail.html', {
        'contract': contract,
        'milestones': milestones,
        'amendments': amendments,
        'lifecycle_logs': lifecycle_logs,
        'invoices': invoices,
        'inspection_certs': inspection_certs,
        'milestone_form': milestone_form,
        'amendment_form': amendment_form,
        'status_choices': Contract.STATUS_CHOICES,
    })

@login_required
def contract_create(request):
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            if not contract.contracting_officer:
                contract.contracting_officer = request.user
            contract.save()

            ContractLifecycleLog.objects.create(
                contract=contract,
                from_status='NONE',
                to_status=contract.contract_status,
                changed_by=request.user,
                notes="Initial defense contract record registered in system."
            )
            AuditLog.objects.create(
                user=request.user,
                action='CREATE_CONTRACT',
                module='CONTRACTS',
                target_id=contract.contract_number,
                target_repr=contract.title,
                details=f"Drafted defense contract for {contract.vendor.name}. Value: ₹{contract.total_contract_value}.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Contract {contract.contract_number} created successfully.")
            return redirect('contract_detail', pk=contract.pk)
    else:
        form = ContractForm()
    return render(request, 'contracts/contract_form.html', {'form': form, 'title': 'Draft Defense Procurement Contract'})

@login_required
def contract_edit(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if request.method == 'POST':
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            contract = form.save()
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE_CONTRACT',
                module='CONTRACTS',
                target_id=contract.contract_number,
                target_repr=contract.title,
                details=f"Updated parameters for contract {contract.contract_number}.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Contract {contract.contract_number} updated.")
            return redirect('contract_detail', pk=contract.pk)
    else:
        form = ContractForm(instance=contract)
    return render(request, 'contracts/contract_form.html', {'form': form, 'title': f'Edit Contract: {contract.contract_number}', 'contract': contract})

@login_required
def contract_change_status(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        notes = request.POST.get('notes', '')
        old_status = contract.contract_status

        if new_status and new_status != old_status:
            contract.contract_status = new_status
            contract.save(update_fields=['contract_status', 'updated_at'])

            ContractLifecycleLog.objects.create(
                contract=contract,
                from_status=old_status,
                to_status=new_status,
                changed_by=request.user,
                notes=notes
            )
            AuditLog.objects.create(
                user=request.user,
                action='LIFECYCLE_TRANSITION',
                module='CONTRACTS',
                target_id=contract.contract_number,
                target_repr=contract.title,
                details=f"Transitioned status: {old_status} -> {new_status}. Notes: {notes}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Contract status updated to '{contract.get_contract_status_display()}'.")
    return redirect('contract_detail', pk=contract.pk)

@login_required
def contract_milestone_create(request, contract_pk):
    contract = get_object_or_404(Contract, pk=contract_pk)
    if request.method == 'POST':
        form = ContractMilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.contract = contract
            milestone.save()
            AuditLog.objects.create(
                user=request.user,
                action='CREATE_MILESTONE',
                module='CONTRACTS',
                target_id=contract.contract_number,
                target_repr=milestone.title,
                details=f"Added Milestone {milestone.milestone_number} ({milestone.title}) for ₹{milestone.milestone_amount}.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Milestone M{milestone.milestone_number} added.")
    return redirect('contract_detail', pk=contract.pk)

@login_required
def contract_milestone_submit(request, pk):
    milestone = get_object_or_404(ContractMilestone, pk=pk)
    if request.method == 'POST':
        milestone.status = 'DELIVERABLE_SUBMITTED'
        milestone.save(update_fields=['status'])
        AuditLog.objects.create(
            user=request.user,
            action='SUBMIT_DELIVERABLE',
            module='CONTRACTS',
            target_id=milestone.contract.contract_number,
            target_repr=milestone.title,
            details=f"Deliverables submitted for Milestone M{milestone.milestone_number}. Ready for military inspection.",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, f"Milestone M{milestone.milestone_number} marked as DELIVERABLE SUBMITTED. Ready for DGQA / DD-250 inspection.")
    return redirect('contract_detail', pk=milestone.contract.pk)

@login_required
def contract_amendment_create(request, contract_pk):
    contract = get_object_or_404(Contract, pk=contract_pk)
    if request.method == 'POST':
        form = ContractAmendmentForm(request.POST)
        if form.is_valid():
            amd = form.save(commit=False)
            amd.contract = contract
            amd.approved_by = request.user
            amd.save()

            if amd.status == 'APPROVED':
                # Apply financial impact to contract value
                if amd.financial_impact != 0:
                    contract.total_contract_value += amd.financial_impact
                # Apply time extension
                if amd.new_end_date:
                    contract.end_date = amd.new_end_date
                contract.contract_status = 'AMENDED'
                contract.save()

            AuditLog.objects.create(
                user=request.user,
                action='CONTRACT_AMENDMENT',
                module='CONTRACTS',
                target_id=contract.contract_number,
                target_repr=amd.amendment_number,
                details=f"Executed Amendment {amd.amendment_number} ({amd.get_amendment_type_display()}). Financial delta: ₹{amd.financial_impact}.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Contract Amendment {amd.amendment_number} processed successfully.")
    return redirect('contract_detail', pk=contract.pk)

@login_required
def export_contracts_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="defense_contracts_repository.csv"'
    writer = csv.writer(response)
    writer.writerow(['Contract #', 'Title', 'Prime Contractor', 'Category', 'Classification', 'Total Value (INR)', 'Status', 'Start Date', 'End Date', 'ITAR Controlled'])

    for c in Contract.objects.all().select_related('vendor'):
        writer.writerow([
            c.contract_number, c.title, c.vendor.name, c.get_category_display(),
            c.get_security_classification_display(), c.total_contract_value,
            c.get_contract_status_display(), c.start_date, c.end_date, 'YES' if c.itar_controlled else 'NO'
        ])
    return response
