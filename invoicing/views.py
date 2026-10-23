import csv
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q, Sum

from .models import InspectionCertificate, Invoice, PaymentDisbursement
from .forms import InspectionCertificateForm, InvoiceForm, PaymentDisbursementForm
from contracts.models import Contract, ContractMilestone
from core.models import AuditLog

# --- DD-250 Inspection Certificates ---

@login_required
def inspection_list(request):
    certs = InspectionCertificate.objects.all().select_related('contract', 'milestone', 'inspector')
    q = request.GET.get('q')
    status = request.GET.get('status')

    if q:
        certs = certs.filter(
            Q(certificate_number__icontains=q) |
            Q(qa_report_number__icontains=q) |
            Q(contract__contract_number__icontains=q) |
            Q(inspection_location__icontains=q)
        )
    if status:
        certs = certs.filter(status=status)

    return render(request, 'invoicing/inspection_list.html', {
        'certificates': certs,
        'statuses': InspectionCertificate.STATUS_CHOICES,
        'search_query': q or '',
        'selected_status': status or '',
    })

@login_required
def inspection_detail(request, pk):
    cert = get_object_or_404(InspectionCertificate, pk=pk)
    return render(request, 'invoicing/inspection_detail.html', {'cert': cert})

@login_required
def inspection_create(request):
    milestone_id = request.GET.get('milestone_id')
    contract_id = request.GET.get('contract_id')
    initial_data = {'inspection_date': date.today()}

    if milestone_id:
        milestone = get_object_or_404(ContractMilestone, pk=milestone_id)
        initial_data['milestone'] = milestone
        initial_data['contract'] = milestone.contract
        initial_data['certificate_number'] = f"DD250-2026-{milestone.id:04d}"
    elif contract_id:
        contract = get_object_or_404(Contract, pk=contract_id)
        initial_data['contract'] = contract

    if request.method == 'POST':
        form = InspectionCertificateForm(request.POST)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.inspector = request.user
            cert.save()

            AuditLog.objects.create(
                user=request.user,
                action='CREATE_INSPECTION_CERT',
                module='INVOICING',
                target_id=cert.certificate_number,
                target_repr=f"DD-250 for {cert.contract.contract_number}",
                details=f"Issued inspection certificate ({cert.get_status_display()}) with QA Report {cert.qa_report_number}.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"DD-250 Inspection Certificate {cert.certificate_number} recorded successfully!")
            return redirect('inspection_detail', pk=cert.pk)
    else:
        form = InspectionCertificateForm(initial=initial_data)
    return render(request, 'invoicing/inspection_form.html', {'form': form, 'title': 'Execute DD-250 Military Quality Inspection'})

# --- Invoices & 3-Way Match ---

@login_required
def invoice_list(request):
    invoices = Invoice.objects.all().select_related('contract', 'vendor', 'milestone')
    q = request.GET.get('q')
    status = request.GET.get('status')
    vendor_id = request.GET.get('vendor')

    if q:
        invoices = invoices.filter(
            Q(invoice_number__icontains=q) |
            Q(contract__contract_number__icontains=q) |
            Q(vendor__name__icontains=q)
        )
    if status:
        invoices = invoices.filter(payment_status=status)
    if vendor_id:
        invoices = invoices.filter(vendor_id=vendor_id)

    total_gross = invoices.aggregate(Sum('gross_amount'))['gross_amount__sum'] or 0
    total_net = invoices.aggregate(Sum('net_payable_amount'))['net_payable_amount__sum'] or 0

    return render(request, 'invoicing/invoice_list.html', {
        'invoices': invoices,
        'statuses': Invoice.STATUS_CHOICES,
        'total_gross': total_gross,
        'total_net': total_net,
        'search_query': q or '',
        'selected_status': status or '',
    })

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    disbursements = invoice.disbursements.all().order_by('-disbursement_date')
    disbursement_form = PaymentDisbursementForm(initial={
        'disbursement_date': date.today(),
        'amount': invoice.net_payable_amount,
        'disbursement_reference': f"DEF-PCDA-RTGS-{invoice.id:04d}"
    })
    return render(request, 'invoicing/invoice_detail.html', {
        'invoice': invoice,
        'disbursements': disbursements,
        'disbursement_form': disbursement_form,
    })

@login_required
def invoice_create(request):
    milestone_id = request.GET.get('milestone_id')
    contract_id = request.GET.get('contract_id')
    initial_data = {
        'invoice_date': date.today(),
        'due_date': date.today(),
    }

    if milestone_id:
        milestone = get_object_or_404(ContractMilestone, pk=milestone_id)
        initial_data['milestone'] = milestone
        initial_data['contract'] = milestone.contract
        initial_data['vendor'] = milestone.contract.vendor
        initial_data['gross_amount'] = milestone.milestone_amount
        initial_data['invoice_number'] = f"INV-{milestone.contract.vendor.vendor_code}-{milestone.id:03d}"
        
        # Link latest inspection cert if exists
        passed_cert = milestone.inspections.filter(status='PASSED').first()
        if passed_cert:
            initial_data['inspection_cert'] = passed_cert

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            if invoice.milestone:
                invoice.milestone.status = 'INVOICED'
                invoice.milestone.save(update_fields=['status'])

            AuditLog.objects.create(
                user=request.user,
                action='SUBMIT_INVOICE',
                module='INVOICING',
                target_id=invoice.invoice_number,
                target_repr=f"Invoice for {invoice.vendor.name}",
                details=f"Submitted defense payment claim of ₹{invoice.net_payable_amount} (Gross: ₹{invoice.gross_amount}).",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Invoice {invoice.invoice_number} submitted.")
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(initial=initial_data)
    return render(request, 'invoicing/invoice_form.html', {'form': form, 'title': 'Generate Defense Procurement Invoice'})

@login_required
def invoice_verify_three_way(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'VERIFY':
            # Run 3-Way Match Validation
            has_contract = invoice.contract is not None
            has_inspection = invoice.inspection_cert is not None and invoice.inspection_cert.status == 'PASSED'
            
            if has_contract and has_inspection:
                invoice.payment_status = 'THREE_WAY_MATCH_VERIFIED'
                invoice.save(update_fields=['payment_status'])
                AuditLog.objects.create(
                    user=request.user,
                    action='THREE_WAY_MATCH_PASSED',
                    module='INVOICING',
                    target_id=invoice.invoice_number,
                    target_repr=f"Verified 3-Way Match for {invoice.invoice_number}",
                    details="Automated 3-Way reconciliation passed: Contract PO + DD-250 Inspection + Invoice amount match.",
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.success(request, f"3-Way Match VERIFIED successfully for Invoice {invoice.invoice_number}!")
            else:
                messages.error(request, "3-Way Match Verification Failed: Contract or Approved DD-250 certificate is missing.")
        elif action == 'AUDIT_APPROVE':
            invoice.payment_status = 'AUDIT_APPROVED'
            invoice.save(update_fields=['payment_status'])
            AuditLog.objects.create(
                user=request.user,
                action='AUDIT_APPROVE_INVOICE',
                module='INVOICING',
                target_id=invoice.invoice_number,
                target_repr=f"Approved by Finance Auditor {request.user.username}",
                details="Passed financial audit check. Sanctioned for treasury disbursement.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Invoice {invoice.invoice_number} approved for payment release.")
    return redirect('invoice_detail', pk=invoice.pk)

# --- Payment Disbursements ---

@login_required
def payment_disbursement_create(request, invoice_pk):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    if request.method == 'POST':
        form = PaymentDisbursementForm(request.POST)
        if form.is_valid():
            disb = form.save(commit=False)
            disb.invoice = invoice
            disb.disbursed_by = request.user
            disb.save()

            AuditLog.objects.create(
                user=request.user,
                action='DISBURSE_PAYMENT',
                module='INVOICING',
                target_id=disb.disbursement_reference,
                target_repr=f"Treasury Payment of ₹{disb.amount}",
                details=f"Disbursed payment via {disb.get_payment_method_display()} (Ref: {disb.bank_reference}) to {invoice.vendor.name}.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Payment of ₹{disb.amount} successfully disbursed! Reference: {disb.disbursement_reference}.")
            return redirect('invoice_detail', pk=invoice.pk)
    return redirect('invoice_detail', pk=invoice.pk)

@login_required
def export_invoices_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="defense_invoices_ledger.csv"'
    writer = csv.writer(response)
    writer.writerow(['Invoice #', 'Contract #', 'Vendor', 'Milestone', 'Invoice Date', 'Gross Amount', 'Retention 5%', 'Net Payable', 'Status', 'DD-250 Cert'])

    for inv in Invoice.objects.all().select_related('contract', 'vendor', 'milestone', 'inspection_cert'):
        writer.writerow([
            inv.invoice_number,
            inv.contract.contract_number,
            inv.vendor.name,
            inv.milestone.title if inv.milestone else 'N/A',
            inv.invoice_date,
            inv.gross_amount,
            inv.withholding_amount,
            inv.net_payable_amount,
            inv.get_payment_status_display(),
            inv.inspection_cert.certificate_number if inv.inspection_cert else 'None'
        ])
    return response
