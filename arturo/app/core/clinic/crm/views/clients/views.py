import json

from django.contrib.auth.models import Group
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from config import settings
from core.clinic.crm.forms import User, Parish, ClientsForm
from core.security.mixins import AccessModuleMixin


class ClientsListView(AccessModuleMixin, ListView):
    model = User
    template_name = 'clients/list.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search':
                data = []
                pos = 1
                for i in User.objects.filter(groups__in=[settings.GROUPS.get('client')]):
                    item = i.toJSON()
                    item['pos'] = pos
                    data.append(item)
                    pos += 1
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('clients_create')
        context['title'] = 'Listado de Clientes'
        return context


class ClientsCreateView(AccessModuleMixin, CreateView):
    model = User
    template_name = 'clients/create.html'
    form_class = ClientsForm
    success_url = reverse_lazy('clients_list')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            obj = self.request.POST['obj'].strip()
            if type == 'dni':
                if User.objects.filter(dni__iexact=obj):
                    data['valid'] = False
            elif type == 'email':
                if User.objects.filter(email=obj):
                    data['valid'] = False
            elif type == 'mobile_phone':
                if User.objects.filter(mobile_phone=obj):
                    data['valid'] = False
            elif type == 'landline':
                if User.objects.filter(landline=obj):
                    data['valid'] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'add':
                with transaction.atomic():
                    user = User()
                    user.first_name = request.POST['first_name']
                    user.last_name = request.POST['last_name']
                    user.dni = request.POST['dni']
                    if 'image-clear' in request.POST:
                        user.remove_image()
                        user.image = None
                    if 'image' in request.FILES:
                        user.image = request.FILES['image']
                    user.create_or_update_password(request.POST['password'])
                    user.email = request.POST['email']
                    # user.parish_id = request.POST['parish']
                    user.gender = request.POST['gender']
                    user.mobile_phone = request.POST['mobile_phone']
                    user.landline = request.POST['landline']
                    user.address = request.POST['address']
                    user.landline = request.POST['landline']
                    user.birthdate = request.POST['birthdate']
                    user.save()

                    group = Group.objects.get(pk=settings.GROUPS.get('client'))
                    user.groups.add(group)
            elif action == 'validate_data':
                return self.validate_data()
            # elif action == 'search_parish':
            #     data = []
            #     term = request.POST['term']
            #     for i in Parish.objects.filter(name__icontains=term)[0:10]:
            #         item = {'id': i.id, 'text': i.__str__(), 'data': i.toJSON()}
            #         data.append(item)
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de un Cliente'
        context['action'] = 'add'
        return context


class ClientsUpdateView(AccessModuleMixin, UpdateView):
    model = User
    template_name = 'clients/create.html'
    form_class = ClientsForm
    success_url = reverse_lazy('clients_list')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        instance = self.get_object()
        form = ClientsForm(instance=instance)
        CHOICES = [
            (instance.parish.id, instance.parish.__str__()),
        ]
        form.fields['parish'].choices = CHOICES
        return form

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            id = self.get_object().id
            obj = self.request.POST['obj'].strip()
            if type == 'dni':
                if User.objects.filter(dni__iexact=obj).exclude(id=id):
                    data['valid'] = False
            elif type == 'email':
                if User.objects.filter(email=obj).exclude(id=id):
                    data['valid'] = False
            elif type == 'mobile_phone':
                if User.objects.filter(mobile_phone=obj).exclude(id=id):
                    data['valid'] = False
            elif type == 'landline':
                if User.objects.filter(landline=obj).exclude(id=id):
                    data['valid'] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'edit':
                with transaction.atomic():
                    user = self.get_object().user
                    user.first_name = request.POST['first_name']
                    user.last_name = request.POST['last_name']
                    user.dni = request.POST['dni']
                    if 'image-clear' in request.POST:
                        user.remove_image()
                        user.image = None
                    if 'image' in request.FILES:
                        user.image = request.FILES['image']
                    user.create_or_update_password(request.POST['password'])
                    user.email = request.POST['email']
                    user.parish_id = request.POST['parish']
                    user.gender = request.POST['gender']
                    user.mobile_phone = request.POST['mobile_phone']
                    user.landline = request.POST['landline']
                    user.address = request.POST['address']
                    user.landline = request.POST['landline']
                    user.birthdate = request.POST['birthdate']
                    user.save()
            elif action == 'validate_data':
                return self.validate_data()
            elif action == 'search_parish':
                data = []
                term = request.POST['term']
                for i in Parish.objects.filter(name__icontains=term)[0:10]:
                    item = {'id': i.id, 'text': i.__str__(), 'data': i.toJSON()}
                    data.append(item)
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Edición de un Cliente'
        context['action'] = 'edit'
        return context


class ClientsDeleteView(AccessModuleMixin, DeleteView):
    model = User
    template_name = 'clients/delete.html'
    success_url = reverse_lazy('clients_list')

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
