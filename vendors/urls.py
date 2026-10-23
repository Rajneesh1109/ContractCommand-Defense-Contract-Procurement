from django.urls import path
from . import views

urlpatterns = [
    path('', views.vendor_list, name='vendor_list'),
    path('register/', views.vendor_create, name='vendor_create'),
    path('<int:pk>/', views.vendor_detail, name='vendor_detail'),
    path('<int:pk>/edit/', views.vendor_edit, name='vendor_edit'),
    path('<int:vendor_pk>/evaluate/', views.vendor_evaluation_create, name='vendor_evaluation_create'),
    path('export/', views.export_vendors_csv, name='export_vendors'),
]
