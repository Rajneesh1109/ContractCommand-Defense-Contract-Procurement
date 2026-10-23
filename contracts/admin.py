from django.contrib import admin
from .models import Contract, ContractMilestone, ContractAmendment, ContractLifecycleLog

class ContractMilestoneInline(admin.TabularInline):
    model = ContractMilestone
    extra = 0
    fields = ('milestone_number', 'title', 'due_date', 'weightage_percentage', 'milestone_amount', 'status')

class ContractAmendmentInline(admin.TabularInline):
    model = ContractAmendment
    extra = 0

class ContractLifecycleLogInLine(admin.TabularInline):
    model = ContractLifecycleLog
    extra = 0
    readonly_fields = ('from_status', 'to_status', 'changed_by', 'notes', 'timestamp')
    can_delete = False

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'title', 'vendor', 'category', 'security_classification', 'total_contract_value', 'contract_status', 'end_date')
    list_filter = ('category', 'security_classification', 'contract_status', 'itar_controlled')
    search_fields = ('contract_number', 'title', 'vendor__name', 'scope_of_contract')
    inlines = [ContractMilestoneInline, ContractAmendmentInline, ContractLifecycleLogInLine]

@admin.register(ContractMilestone)
class ContractMilestoneAdmin(admin.ModelAdmin):
    list_display = ('contract', 'milestone_number', 'title', 'due_date', 'milestone_amount', 'status')
    list_filter = ('status', 'due_date')
    search_fields = ('contract__contract_number', 'title', 'description')

@admin.register(ContractAmendment)
class ContractAmendmentAdmin(admin.ModelAdmin):
    list_display = ('contract', 'amendment_number', 'amendment_type', 'financial_impact', 'new_end_date', 'status')
    list_filter = ('amendment_type', 'status')
    search_fields = ('contract__contract_number', 'amendment_number', 'description')
