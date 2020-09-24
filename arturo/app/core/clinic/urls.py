from django.urls import include, path

urlpatterns = [
    path('crm/', include('core.clinic.crm.urls')),
    path('scm/', include('core.clinic.scm.urls')),
]
