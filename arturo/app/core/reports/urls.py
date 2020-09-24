from django.urls import path
from .views.purchase_report.views import PurchaseReportView
from .views.datemedical_report.views import DateMedicalReportView
from .views.sale_report.views import SaleReportView

urlpatterns = [
    path('purchase/', PurchaseReportView.as_view(), name='purchase_report'),
    path('datemedical/', DateMedicalReportView.as_view(), name='datemedical_report'),
    path('sale/', SaleReportView.as_view(), name='sale_report'),
]
