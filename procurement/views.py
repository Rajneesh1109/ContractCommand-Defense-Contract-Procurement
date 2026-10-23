import csv
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q

from .models import ProcurementRequisition, RequisitionItem, TenderRFP, TenderBid, DefenseItemCatalog
from .forms import ProcurementRequisitionForm, RequisitionItemForm, TenderRFPForm, TenderBidForm, DefenseCatalogForm
from contracts.models import Contract
from core.models import AuditLog

# --- Requisitions ---

@login_required
def requisition_list(request):
    reqs = ProcurementRequisition.objects.all().select_related('created_by', 'approved_by')
    q = request.GET.get('q')
    category = request.GET.get('category')
    priority = request.GET.get('priority')
    status = request.GET.get('status')

    if q:
        reqs = reqs.filter(Q(requisition_number__icontains=q) | Q(title__icontains=q) | Q(demanding_service__icontains=q))
    if category:
        reqs = reqs.filter(category=category)
    if priority:
        reqs = reqs.filter(priority=priority)
    if status:
        reqs = reqs.filter(status=status)

    return render(request, 'procurement/requisition_list.html', {
        'requisitions': reqs,
        'categories': DefenseItemCatalog.CATEGORY_CHOICES,
        'priorities': ProcurementRequisition.PRIORITY_CHOICES,
        'statuses': ProcurementRequisition.STATUS_CHOICES,
        'search_query': q or '',
        'selected_category': category or '',
        'selected_priority': priority or '',
        'selected_status': status or '',
    })

@login_required
def requisition_detail(request, pk):
    requisition = get_object_or_404(ProcurementRequisition, pk=pk)
    item_form = RequisitionItemForm()

    if request.method == 'POST' and 'add_item' in request.POST:
        item_form = RequisitionItemForm(request.POST)
        if item_form.is_valid():
            item = item_form.save(commit=False)
            item.requisition = requisition
            item.save()
            # Recalculate estimated total cost
            total = sum(i.total_price for i in requisition.items.all())
            requisition.estimated_total_cost = total
            requisition.save(update_fields=['estimated_total_cost'])
            messages.success(request, f"Added line item: {item.description}")
            return redirect('requisition_detail', pk=requisition.pk)

    return render(request, 'procurement/requisition_detail.html', {
        'requisition': requisition,
        'item_form': item_form,
    })

@login_required
def requisition_create(request):
    if request.method == 'POST':
        form = ProcurementRequisitionForm(request.POST)
        if form.is_valid():
            requisition = form.save(commit=False)
            requisition.created_by = request.user
            requisition.save()
            AuditLog.objects.create(
                user=request.user,
                action='CREATE_REQUISITION',
                module='PROCUREMENT',
                target_id=requisition.requisition_number,
                target_repr=requisition.title,
                details=f"Raised defense procurement requisition for {requisition.demanding_service}. Priority: {requisition.get_priority_display()}.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Procurement requisition {requisition.requisition_number} initiated.")
            return redirect('requisition_detail', pk=requisition.pk)
    else:
        form = ProcurementRequisitionForm()
    return render(request, 'procurement/requisition_form.html', {'form': form, 'title': 'Raise Defense Procurement Requisition'})

@login_required
def requisition_approve(request, pk):
    requisition = get_object_or_404(ProcurementRequisition, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('approval_notes', '')
        if action == 'APPROVE':
            requisition.status = 'APPROVED'
            requisition.approved_by = request.user
            requisition.approval_date = date.today()
            requisition.approval_notes = notes
            requisition.save()
            AuditLog.objects.create(
                user=request.user,
                action='APPROVE_REQUISITION',
                module='PROCUREMENT',
                target_id=requisition.requisition_number,
                target_repr=requisition.title,
                details=f"Requisition approved by {request.user.username}. Notes: {notes}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Requisition {requisition.requisition_number} has been officially approved.")
        elif action == 'REJECT':
            requisition.status = 'REJECTED'
            requisition.approval_notes = notes
            requisition.save()
            messages.warning(request, f"Requisition {requisition.requisition_number} rejected.")
    return redirect('requisition_detail', pk=requisition.pk)

# --- Tenders & RFPs ---

@login_required
def tender_list(request):
    tenders = TenderRFP.objects.all().select_related('requisition', 'created_by')
    q = request.GET.get('q')
    tender_type = request.GET.get('tender_type')
    status = request.GET.get('status')

    if q:
        tenders = tenders.filter(Q(tender_number__icontains=q) | Q(title__icontains=q))
    if tender_type:
        tenders = tenders.filter(tender_type=tender_type)
    if status:
        tenders = tenders.filter(status=status)

    return render(request, 'procurement/tender_list.html', {
        'tenders': tenders,
        'types': TenderRFP.TENDER_TYPE_CHOICES,
        'statuses': TenderRFP.STATUS_CHOICES,
        'search_query': q or '',
        'selected_type': tender_type or '',
        'selected_status': status or '',
    })

@login_required
def tender_detail(request, pk):
    tender = get_object_or_404(TenderRFP, pk=pk)
    bids = tender.bids.all().select_related('vendor').order_by('bid_amount')
    bid_form = TenderBidForm()

    if request.method == 'POST' and 'submit_bid' in request.POST:
        bid_form = TenderBidForm(request.POST)
        if bid_form.is_valid():
            bid = bid_form.save(commit=False)
            bid.tender = tender
            bid.save()
            AuditLog.objects.create(
                user=request.user,
                action='SUBMIT_TENDER_BID',
                module='PROCUREMENT',
                target_id=tender.tender_number,
                target_repr=f"Bid from {bid.vendor.name}",
                details=f"Vendor {bid.vendor.name} submitted bid of ₹{bid.bid_amount}.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Defense bid from {bid.vendor.name} registered.")
            return redirect('tender_detail', pk=tender.pk)

    return render(request, 'procurement/tender_detail.html', {
        'tender': tender,
        'bids': bids,
        'bid_form': bid_form,
    })

@login_required
def tender_create(request):
    req_id = request.GET.get('req_id')
    initial_data = {}
    if req_id:
        req = get_object_or_404(ProcurementRequisition, pk=req_id)
        initial_data = {
            'requisition': req,
            'title': f"RFP: {req.title}",
            'estimated_value': req.estimated_total_cost,
            'publication_date': date.today(),
        }

    if request.method == 'POST':
        form = TenderRFPForm(request.POST)
        if form.is_valid():
            tender = form.save(commit=False)
            tender.created_by = request.user
            tender.save()
            if tender.requisition:
                tender.requisition.status = 'TENDER_ISSUED'
                tender.requisition.save()
            AuditLog.objects.create(
                user=request.user,
                action='PUBLISH_TENDER',
                module='PROCUREMENT',
                target_id=tender.tender_number,
                target_repr=tender.title,
                details=f"Published defense tender {tender.tender_number}. Value: ₹{tender.estimated_value}.",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Defense Tender {tender.tender_number} published successfully.")
            return redirect('tender_detail', pk=tender.pk)
    else:
        form = TenderRFPForm(initial=initial_data)
    return render(request, 'procurement/tender_form.html', {'form': form, 'title': 'Publish Defense Tender / RFP Notice'})

@login_required
def tender_award(request, pk, bid_pk):
    tender = get_object_or_404(TenderRFP, pk=pk)
    bid = get_object_or_404(TenderBid, pk=bid_pk, tender=tender)

    if request.method == 'POST':
        bid.bid_status = 'ACCEPTED_L1'
        bid.save()
        # Mark other bids as rejected
        tender.bids.exclude(pk=bid.pk).update(bid_status='REJECTED')
        tender.status = 'AWARDED'
        tender.save()

        AuditLog.objects.create(
            user=request.user,
            action='AWARD_TENDER',
            module='PROCUREMENT',
            target_id=tender.tender_number,
            target_repr=tender.title,
            details=f"Awarded tender to lowest compliant bidder: {bid.vendor.name} for ₹{bid.bid_amount}.",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, f"Tender {tender.tender_number} awarded to Prime Contractor {bid.vendor.name} (L1 Bid: ₹{bid.bid_amount}).")
    return redirect('tender_detail', pk=tender.pk)

# --- Defense Catalog ---

@login_required
def catalog_list(request):
    items = DefenseItemCatalog.objects.all()
    q = request.GET.get('q')
    category = request.GET.get('category')

    if q:
        items = items.filter(Q(item_code__icontains=q) | Q(name__icontains=q) | Q(specifications__icontains=q))
    if category:
        items = items.filter(category=category)

    return render(request, 'procurement/catalog_list.html', {
        'items': items,
        'categories': DefenseItemCatalog.CATEGORY_CHOICES,
        'search_query': q or '',
        'selected_category': category or '',
    })

@login_required
def catalog_create(request):
    if request.method == 'POST':
        form = DefenseCatalogForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f"Defense catalog item {item.item_code} added.")
            return redirect('catalog_list')
    else:
        form = DefenseCatalogForm()
    return render(request, 'procurement/catalog_form.html', {'form': form, 'title': 'Add Equipment to Defense Catalog'})
