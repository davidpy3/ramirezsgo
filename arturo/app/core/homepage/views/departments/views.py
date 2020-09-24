import json

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.homepage.forms import Departments, DepartmentsForm
from core.security.mixins import AccessModuleMixin, PermissionModuleMixin


class DepartmentsListView(AccessModuleMixin, PermissionModuleMixin, ListView):
    model = Departments
    template_name = 'departments/list.html'
    permission_required = 'view_departments'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('departments_create')
        context['title'] = 'Listado de Departamentos'
        return context


class DepartmentsCreateView(AccessModuleMixin, PermissionModuleMixin, CreateView):
    model = Departments
    template_name = 'departments/create.html'
    form_class = DepartmentsForm
    success_url = reverse_lazy('departments_list')
    permission_required = 'add_departments'

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
        context['title'] = 'Nuevo registro de un Departamento'
        context['action'] = 'add'
        return context


class DepartmentsUpdateView(AccessModuleMixin, PermissionModuleMixin, UpdateView):
    model = Departments
    template_name = 'departments/create.html'
    form_class = DepartmentsForm
    success_url = reverse_lazy('departments_list')
    permission_required = 'change_departments'

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
        context['title'] = 'Edición de un Departamento'
        context['action'] = 'edit'
        return context


class DepartmentsDeleteView(AccessModuleMixin, PermissionModuleMixin, DeleteView):
    model = Departments
    template_name = 'departments/delete.html'
    success_url = reverse_lazy('departments_list')
    permission_required = 'delete_departments'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            Departments.objects.get(pk=self.get_object().id).delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificación de eliminación'
        context['list_url'] = self.success_url
        return context
