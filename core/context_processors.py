from contracts.models import Contract
from invoicing.models import Invoice

def defense_system_info(request):
    active_contracts_count = 0
    pending_invoices_count = 0
    try:
        active_contracts_count = Contract.objects.filter(contract_status__in=['ACTIVE', 'AMENDED']).count()
        pending_invoices_count = Invoice.objects.filter(payment_status__in=['SUBMITTED', 'THREE_WAY_MATCH_VERIFIED']).count()
    except Exception:
        pass
    
    return {
        'APP_NAME': 'ContractCommand',
        'SYSTEM_SUBTITLE': 'Defense Contract & Procurement Lifecycle Management',
        'DEFENSE_CLASSIFICATION': 'RESTRICTED // DEFENSE PROCUREMENT NETWORK',
        'ACTIVE_CONTRACTS_NAV_COUNT': active_contracts_count,
        'PENDING_INVOICES_NAV_COUNT': pending_invoices_count,
    }
