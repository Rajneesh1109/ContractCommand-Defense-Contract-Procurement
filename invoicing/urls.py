from django.urls import path
from . import views

urlpatterns = [
    # Inspections (DD-250)
    path('inspections/', views.inspection_list, name='inspection_list'),
    path('inspections/new/', views.inspection_create, name='inspection_create'),
    path('inspections/<int:pk>/', views.inspection_detail, name='inspection_detail'),

    # Invoices & 3-Way Match
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/new/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/verify/', views.invoice_verify_three_way, name='invoice_verify_three_way'),
    path('invoices/<int:invoice_pk>/disburse/', views.payment_disbursement_create, name='payment_disbursement_create'),
    path('invoices/export/', views.export_invoices_csv, name='export_invoices'),
]
