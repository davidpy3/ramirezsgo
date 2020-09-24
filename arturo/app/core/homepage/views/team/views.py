import json

from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.homepage.forms import Team, TeamForm, TeamSocialNet
from core.security.mixins import AccessModuleMixin, PermissionModuleMixin


class TeamListView(AccessModuleMixin, PermissionModuleMixin, ListView):
    model = Team
    template_name = 'team/list.html'
    permission_required = 'view_team'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('team_create')
        context['title'] = 'Listado de Doctores'
        return context


class TeamCreateView(AccessModuleMixin, PermissionModuleMixin, CreateView):
    model = Team
    template_name = 'team/create.html'
    form_class = TeamForm
    success_url = reverse_lazy('team_list')
    permission_required = 'add_team'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', None)
        data = {}
        try:
            if action == 'add':
                with transaction.atomic():
                    t = Team()
                    t.names = request.POST['names']
                    t.job = request.POST['job']
                    t.desc = request.POST['desc']
                    t.phrase = request.POST['phrase']
                    t.state = request.POST['state']
                    if 'image' in request.FILES:
                        t.image = request.FILES['image']
                    t.save()
                    team = json.loads(request.POST['socialnet'])
                    for s in team:
                        det = TeamSocialNet()
                        det.team = t
                        det.icon = s['icon']
                        det.name = s['name']
                        det.url = s['url']
                        det.save()
            else:
                data['error'] = 'No ha ingresado una opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de un Doctor'
        context['action'] = 'add'
        context['social'] = []
        return context


class TeamUpdateView(AccessModuleMixin, PermissionModuleMixin, UpdateView):
    model = Team
    template_name = 'team/create.html'
    form_class = TeamForm
    success_url = reverse_lazy('team_list')
    permission_required = 'change_team'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_socialnet(self):
        data = []
        try:
            team = Team.objects.get(pk=self.kwargs['pk'])
            for i in team.teamsocialnet_set.all():
                data.append(i.toJSON())
        except:
            pass
        return data

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', None)
        data = {}
        try:
            if action == 'edit':
                with transaction.atomic():
                    t = Team.objects.get(pk=self.get_object().id)
                    t.names = request.POST['names']
                    t.job = request.POST['job']
                    t.desc = request.POST['desc']
                    t.phrase = request.POST['phrase']
                    t.state = request.POST['state']
                    if 'image' in request.FILES:
                        t.image = request.FILES['image']
                    t.save()
                    t.teamsocialnet_set.all().delete()
                    team = json.loads(request.POST['socialnet'])
                    for s in team:
                        det = TeamSocialNet()
                        det.team = t
                        det.icon = s['icon']
                        det.name = s['name']
                        det.url = s['url']
                        det.save()
            else:
                data['error'] = 'No ha ingresado una opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Edición de un Doctor'
        context['action'] = 'edit'
        context['social'] = json.dumps(self.get_socialnet())
        return context


class TeamDeleteView(AccessModuleMixin, PermissionModuleMixin, DeleteView):
    model = Team
    template_name = 'team/delete.html'
    success_url = reverse_lazy('team_list')
    permission_required = 'delete_team'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            Team.objects.get(pk=self.get_object().id).delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notificación de eliminación'
        context['list_url'] = self.success_url
        return context
