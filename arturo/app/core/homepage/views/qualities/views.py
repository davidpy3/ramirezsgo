import json

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.homepage.forms import Qualities, QualitiesForm
from core.security.mixins import AccessModuleMixin, PermissionModuleMixin


class QualitiesListView(AccessModuleMixin, PermissionModuleMixin, ListView):
    model = Qualities
    template_name = 'qualities/list.html'
    permission_required = 'view_qualities'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('qualities_create')
        context['title'] = 'Listado de Cualidades'
        return context


class QualitiesCreateView(AccessModuleMixin, PermissionModuleMixin, CreateView):
    model = Qualities
    template_name = 'qualities/create.html'
    form_class = QualitiesForm
    success_url = reverse_lazy('qualities_list')
    permission_required = 'add_qualities'

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
        context['title'] = 'Nuevo registro de una Cualidad'
        context['action'] = 'add'
        return context


class QualitiesUpdateView(AccessModuleMixin, PermissionModuleMixin, UpdateView):
    model = Qualities
    template_name = 'qualities/create.html'
    form_class = QualitiesForm
    success_url = reverse_lazy('qualities_list')
    permission_required = 'change_qualities'

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
        context['title'] = 'Edición de una Cualidad'
        context['action'] = 'edit'
        return context


class QualitiesDeleteView(AccessModuleMixin, PermissionModuleMixin, DeleteView):
    model = Qualities
    template_name = 'qualities/delete.html'
    success_url = reverse_lazy('qualities_list')
    permission_required = 'delete_qualities'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            Qualities.objects.get(pk=self.get_object().id).delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificación de eliminación'
        context['list_url'] = self.success_url
        return context
