import json

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.homepage.forms import Services, ServicesForm
from core.security.mixins import AccessModuleMixin, PermissionModuleMixin


class ServicesListView(AccessModuleMixin, PermissionModuleMixin, ListView):
    model = Services
    template_name = 'services/list.html'
    permission_required = 'view_services'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('services_create')
        context['title'] = 'Listado de Servicios'
        return context


class ServicesCreateView(AccessModuleMixin, PermissionModuleMixin, CreateView):
    model = Services
    template_name = 'services/create.html'
    form_class = ServicesForm
    success_url = reverse_lazy('services_list')
    permission_required = 'add_services'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'add':
                data = self.get_form().save()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de un Servicio'
        context['action'] = 'add'
        return context


class ServicesUpdateView(AccessModuleMixin, PermissionModuleMixin, UpdateView):
    model = Services
    template_name = 'services/create.html'
    form_class = ServicesForm
    success_url = reverse_lazy('services_list')
    permission_required = 'change_services'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'edit':
                data = self.get_form().save()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Edición de un Servicio'
        context['action'] = 'edit'
        return context


class ServicesDeleteView(AccessModuleMixin, PermissionModuleMixin, DeleteView):
    model = Services
    template_name = 'services/delete.html'
    success_url = reverse_lazy('services_list')
    permission_required = 'delete_services'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            Services.objects.get(pk=self.get_object().id).delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificación de eliminación'
        context['list_url'] = self.success_url
        return context
