import json

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.homepage.forms import News, NewsForm
from core.security.mixins import AccessModuleMixin, PermissionModuleMixin


class NewsListView(AccessModuleMixin, PermissionModuleMixin, ListView):
    model = News
    template_name = 'news/list.html'
    permission_required = 'view_news'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('news_create')
        context['title'] = 'Listado de Noticias'
        return context


class NewsCreateView(AccessModuleMixin, PermissionModuleMixin, CreateView):
    model = News
    template_name = 'news/create.html'
    form_class = NewsForm
    success_url = reverse_lazy('news_list')
    permission_required = 'add_news'

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
        context['title'] = 'Nuevo registro de un Video'
        context['action'] = 'add'
        return context


class NewsUpdateView(AccessModuleMixin, PermissionModuleMixin, UpdateView):
    model = News
    template_name = 'news/create.html'
    form_class = NewsForm
    success_url = reverse_lazy('news_list')
    permission_required = 'change_news'

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
        context['title'] = 'Edición de un Video'
        context['action'] = 'edit'
        return context


class NewsDeleteView(AccessModuleMixin, PermissionModuleMixin, DeleteView):
    model = News
    template_name = 'news/delete.html'
    success_url = reverse_lazy('news_list')
    permission_required = 'delete_news'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificación de eliminación'
        context['list_url'] = self.success_url
        return context
