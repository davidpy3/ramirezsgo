import json

from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.security.forms import GroupForm
from core.security.mixins import AccessModuleMixin, PermissionModuleMixin
from core.security.models import *


class GroupListView(AccessModuleMixin, PermissionModuleMixin, ListView):
    model = Group
    template_name = 'group/list.html'
    permission_required = 'view_group'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'search_permissions':
                data = []
                for i in Permission.objects.filter(group__in=[request.POST['id']]):
                    data.append({
                        'id': i.id,
                        'name': i.name,
                        'codename': i.codename,
                    })
            elif action == 'search_modules':
                data = []
                for i in Module.objects.filter(groupmodule__groups__in=[request.POST['id']]):
                    data.append(i.toJSON())
            else:
                data['error'] = 'No ha ingresado una opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('group_create')
        context['title'] = 'Listado de Grupos'
        return context


class GroupCreateView(AccessModuleMixin, PermissionModuleMixin, CreateView):
    model = Group
    template_name = 'group/create.html'
    form_class = GroupForm
    success_url = reverse_lazy('group_list')
    permission_required = 'add_group'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            obj = self.request.POST['obj'].strip()
            if type == 'name':
                if Group.objects.filter(name__iexact=obj):
                    data['valid'] = False
        except:
            pass
        return JsonResponse(data)

    def get_permissions(self):
        data = []
        modules = Module.objects.filter().exclude().order_by('name')
        for i in modules:
            info = i.toJSON()
            info['permissions'] = i.get_permission()
            data.append(info)
        return json.dumps(data)

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', None)
        data = {}
        try:
            if action == 'add':
                with transaction.atomic():
                    items = json.loads(request.POST['items'])
                    group = Group()
                    group.name = items['name']
                    group.save()
                    for i in items['permissions']:
                        module = Module.objects.get(pk=i['module_id'])
                        if int(i['content_type_id']) == 0:
                            det = GroupModule()
                            det.groups = group
                            det.modules_id = module.id
                            det.save()
                        else:
                            perm = Permission.objects.get(pk=i['id'])
                            if 'view_' in perm.codename:
                                if not GroupModule.objects.filter(groups_id=group.id, modules_id=module.id).exists():
                                    det = GroupModule()
                                    det.groups = group
                                    det.modules = module
                                    det.save()
                            group.permissions.add(perm)
            elif action == 'validate_data':
                return self.validate_data()
            else:
                data['error'] = 'No ha ingresado una opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['permissions'] = self.get_permissions()
        context['title'] = 'Nuevo registro de un Grupo'
        context['action'] = 'add'
        return context


class GroupUpdateView(AccessModuleMixin, PermissionModuleMixin, UpdateView):
    model = Group
    template_name = 'group/create.html'
    form_class = GroupForm
    success_url = reverse_lazy('group_list')
    permission_required = 'change_group'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            id = self.get_object().id
            obj = self.request.POST['obj'].strip()
            if type == 'name':
                if Group.objects.filter(name__iexact=obj).exclude(id=id):
                    data['valid'] = False
        except:
            pass
        return JsonResponse(data)

    def get_permissions(self):
        data = []
        modules = Module.objects.filter().exclude().order_by('name')
        group = Group.objects.get(pk=self.get_object().id)
        for m in modules:
            permissions = []
            if m.content_type is None:
                obj = m.get_permission()[0]
                obj['state'] = 1 if GroupModule.objects.filter(modules_id=m.id, groups_id=group.id).exists() else 0
                permissions.append(obj)
            else:
                for p in m.get_permission():
                    perm = p
                    if group.permissions.filter(id=p['id'], group__groupmodule__modules_id=m.id).exists():
                        perm['state'] = 1
                    permissions.append(perm)
            item = m.toJSON()
            item['permissions'] = permissions
            data.append(item)
        return json.dumps(data)

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', None)
        data = {}
        try:
            if action == 'edit':
                with transaction.atomic():
                    items = json.loads(request.POST['items'])
                    group = self.get_object()
                    group.name = items['name']
                    group.save()

                    group.groupmodule_set.all().delete()
                    group.permissions.clear()

                    for i in items['permissions']:
                        module = Module.objects.get(pk=i['module_id'])
                        if int(i['content_type_id']) == 0:
                            det = GroupModule()
                            det.groups = group
                            det.modules_id = module.id
                            det.save()
                        else:
                            perm = Permission.objects.get(pk=i['id'])
                            if 'view_' in perm.codename:
                                module = Module.objects.filter(id=i['module_id'])
                                if module.exists():
                                    module = module[0]
                                    if not GroupModule.objects.filter(groups_id=group.id,
                                                                      modules_id=module.id).exists():
                                        det = GroupModule()
                                        det.groups = group
                                        det.modules = module
                                        det.save()
                            group.permissions.add(perm)
            elif action == 'validate_data':
                return self.validate_data()
            else:
                data['error'] = 'No ha ingresado una opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['permissions'] = self.get_permissions()
        context['list_url'] = self.success_url
        context['title'] = 'Edición de un Grupo'
        context['action'] = 'edit'
        return context


class GroupDeleteView(AccessModuleMixin, PermissionModuleMixin, DeleteView):
    model = Group
    template_name = 'group/delete.html'
    success_url = reverse_lazy('group_list')
    permission_required = 'delete_group'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            group = self.get_object()
            group.groupmodule_set.all().delete()
            group.permissions.clear()
            group.delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificación de eliminación'
        context['list_url'] = self.success_url
        return context
