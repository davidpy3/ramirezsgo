from django.urls import path

from core.clinic.crm.views.clients.views import *
from core.clinic.crm.views.datemedical.admin.views import *
from core.clinic.crm.views.datemedical.client.views import *
from core.clinic.crm.views.exam.views import *
from core.clinic.crm.views.historialmedical.client.views import HistorialMedicalClientListView

from core.clinic.crm.views.medicalparameters.views import *
from core.clinic.crm.views.sale.views import *

urlpatterns = [
    # clients
    path('clients/', ClientsListView.as_view(), name='clients_list'),
    path('clients/add/', ClientsCreateView.as_view(), name='clients_create'),
    path('clients/update/<int:pk>/', ClientsUpdateView.as_view(), name='clients_update'),
    path('clients/delete/<int:pk>/', ClientsDeleteView.as_view(), name='clients_delete'),
    # exam
    path('exam/', ExamListView.as_view(), name='exam_list'),
    path('exam/add/', ExamCreateView.as_view(), name='exam_create'),
    path('exam/update/<int:pk>/', ExamUpdateView.as_view(), name='exam_update'),
    path('exam/delete/<int:pk>/', ExamDeleteView.as_view(), name='exam_delete'),
    # medical parameters
    path('medical/parameters/', MedicalParametersListView.as_view(), name='medicalparameters_list'),
    path('medical/parameters/add/', MedicalParametersCreateView.as_view(), name='medicalparameters_create'),
    path('medical/parameters/update/<int:pk>/', MedicalParametersUpdateView.as_view(), name='medicalparameters_update'),
    path('medical/parameters/delete/<int:pk>/', MedicalParametersDeleteView.as_view(), name='medicalparameters_delete'),
    # datemedical/client
    path('date/medical/client/', DateMedicalClientListView.as_view(), name='datemedical_client_list'),
    path('date/medical/client/add/', DateMedicalClientCreateView.as_view(), name='datemedical_client_create'),
    path('date/medical/client/print/<int:pk>/', DateMedicalClientPrintView.as_view(), name='datemedical_client_print'),
    # datemedical/admin
    path('date/medical/admin/', DateMedicalAdminListView.as_view(), name='datemedical_admin_list'),
    path('date/medical/admin/add/', DateMedicalAdminCreateView.as_view(), name='datemedical_admin_create'),
    path('date/medical/admin/update/<int:pk>/', DateMedicalAdminUpdateView.as_view(), name='datemedical_admin_update'),
    path('date/medical/admin/delete/<int:pk>/', DateMedicalAdminDeleteView.as_view(), name='datemedical_admin_delete'),
    path('date/medical/admin/print/<int:pk>/', DateMedicalAdminPrintView.as_view(), name='datemedical_admin_print'),
    # historial/medical/client
    path('historial/medical/client/', HistorialMedicalClientListView.as_view(), name='historial_medical_client_list'),
    # sale
    path('sale/', SaleListView.as_view(), name='sale_list'),
    path('sale/add/', SaleCreateView.as_view(), name='sale_create'),
    path('sale/delete/<int:pk>/', SaleDeleteView.as_view(), name='sale_delete'),
    path('sale/print/invoice/<int:pk>/', SalePrintInvoice.as_view(), name='sale_print'),
]
