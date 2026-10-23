from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('audit-trail/', views.audit_logs_view, name='audit_logs'),
    path('audit-trail/export/', views.export_audit_logs_csv, name='export_audit_logs'),
]
