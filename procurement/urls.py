from django.urls import path
from . import views

urlpatterns = [
    # Requisitions
    path('requisitions/', views.requisition_list, name='requisition_list'),
    path('requisitions/new/', views.requisition_create, name='requisition_create'),
    path('requisitions/<int:pk>/', views.requisition_detail, name='requisition_detail'),
    path('requisitions/<int:pk>/approve/', views.requisition_approve, name='requisition_approve'),

    # Tenders / RFPs
    path('tenders/', views.tender_list, name='tender_list'),
    path('tenders/new/', views.tender_create, name='tender_create'),
    path('tenders/<int:pk>/', views.tender_detail, name='tender_detail'),
    path('tenders/<int:pk>/award/<int:bid_pk>/', views.tender_award, name='tender_award'),

    # Defense Item Catalog
    path('catalog/', views.catalog_list, name='catalog_list'),
    path('catalog/new/', views.catalog_create, name='catalog_create'),
]
