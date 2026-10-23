from django.urls import path
from . import views

urlpatterns = [
    path('', views.contract_list, name='contract_list'),
    path('new/', views.contract_create, name='contract_create'),
    path('<int:pk>/', views.contract_detail, name='contract_detail'),
    path('<int:pk>/edit/', views.contract_edit, name='contract_edit'),
    path('<int:pk>/change-status/', views.contract_change_status, name='contract_change_status'),
    path('<int:contract_pk>/milestones/add/', views.contract_milestone_create, name='contract_milestone_create'),
    path('milestones/<int:pk>/submit/', views.contract_milestone_submit, name='contract_milestone_submit'),
    path('<int:contract_pk>/amendments/add/', views.contract_amendment_create, name='contract_amendment_create'),
    path('export/', views.export_contracts_csv, name='export_contracts'),
]
