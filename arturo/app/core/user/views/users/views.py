import json

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView, View


from core.security.mixins import AccessModuleMixin, PermissionModuleMixin
from core.security.models import *
from core.user.forms import UserForm, ProfileForm
from core.user.models import Parish


class UserListView(AccessModuleMixin, PermissionModuleMixin, ListView):
    model = User
    template_name = 'user/list.html'
    permission_required = 'view_user'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        users = User.objects.filter()
        if self.request.user.is_superuser:
            return users
        return users.filter(is_superuser=False)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'reset_password':
                user = User.objects.get(id=request.POST['id'])
                user.set_password(user.dni)
                user.save()
            elif action == 'login_with_user':
                from django.contrib.auth import login
                admin = User.objects.get(pk=request.POST['id'])
                login(request, admin)
            elif action == 'change_password':
                user = User.objects.get(pk=request.POST['id'])
                user.set_password(request.POST['password'])
                user.save()
                if user == request.user:
                    update_session_auth_hash(request, user)
            elif action == 'search_groups':
                data = User.objects.get(pk=request.POST['id']).get_groups()
            elif action == 'search_access':
                data = User.objects.get(pk=request.POST['id']).get_access_users()
            else:
                data['error'] = 'No ha ingresado una opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('user_create')
        context['title'] = 'Listado de Administradores'
        return context


class UserCreateView(AccessModuleMixin, PermissionModuleMixin, CreateView):
    model = User
    template_name = 'user/create.html'
    form_class = UserForm
    success_url = reverse_lazy('user_list')
    permission_required = 'add_user'

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
                    user.parish_id = request.POST['parish']
                    user.gender = request.POST['gender']
                    user.mobile_phone = request.POST['mobile_phone']
                    user.landline = request.POST['landline']
                    user.address = request.POST['address']
                    user.landline = request.POST['landline']
                    user.birthdate = request.POST['birthdate']
                    user.is_active = 'is_active' in request.POST
                    user.save()
                    for pk in request.POST.getlist('groups'):
                        pk = int(pk)
                        g = Group.objects.get(pk=pk)
                        user.groups.add(g)
            elif action == 'validate_data':
                return self.validate_data()
            elif action == 'search_parish':
                data = []
                term = request.POST['term']
                for i in Parish.objects.filter(name__icontains=term)[0:10]:
                    name = 'Pais: {} / Provincia: {} / Cantón: {} / Parroquia: {}'.format(
                        i.canton.province.country.name, i.canton.province.name, i.canton.name, i.name)
                    item = {'id': i.id, 'text': name, 'data': i.toJSON()}
                    data.append(item)
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de un Administrador'
        context['action'] = 'add'
        return context


class UserUpdateView(AccessModuleMixin, PermissionModuleMixin, UpdateView):
    model = User
    template_name = 'user/create.html'
    form_class = UserForm
    success_url = reverse_lazy('user_list')
    permission_required = 'change_user'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        instance = self.get_object()
        form = UserForm(instance=instance)
        if instance.parish:
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
                    user = self.get_object()
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
                    user.is_active = 'is_active' in request.POST
                    user.save()
                    user.groups.clear()

                    for pk in request.POST.getlist('groups'):
                        pk = int(pk)
                        g = Group.objects.get(pk=pk)
                        user.groups.add(g)

                    if user == request.user:
                        update_session_auth_hash(request, user)
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
        context['title'] = 'Edición de un Administrador'
        context['action'] = 'edit'
        return context


class UserDeleteView(AccessModuleMixin, PermissionModuleMixin, DeleteView):
    model = User
    template_name = 'user/delete.html'
    success_url = reverse_lazy('user_list')
    permission_required = 'delete_user'

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


class UserUpdatePasswordView(AccessModuleMixin, FormView):
    template_name = 'user/change_pwd.html'
    form_class = PasswordChangeForm
    success_url = settings.LOGIN_URL

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = PasswordChangeForm(user=self.request.user)
        form.fields['old_password'].widget.attrs = {
            'class': 'form-control',
            'autocomplete': 'off',
            'placeholder': 'Ingrese su contraseña actual',
        }
        form.fields['new_password1'].widget.attrs = {
            'class': 'form-control',
            'autocomplete': 'off',
            'placeholder': 'Ingrese su nueva contraseña',
        }
        form.fields['new_password2'].widget.attrs = {
            'class': 'form-control',
            'autocomplete': 'off',
            'placeholder': 'Repita su contraseña',
        }
        return form

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'change_pwd':
                form = PasswordChangeForm(user=request.user, data=request.POST)
                if form.is_valid():
                    form.save()
                    update_session_auth_hash(request, form.user)
                else:
                    data['error'] = form.errors
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Cambio de Contraseña'
        context['action'] = 'change_pwd'
        return context


class UserUpdateProfileView(AccessModuleMixin, UpdateView):
    model = User
    template_name = 'user/profile.html'
    form_class = ProfileForm
    success_url = settings.LOGIN_REDIRECT_URL

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            id = self.request.user.id
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

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'edit':
                with transaction.atomic():
                    user = request.user
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
                    if 'profession' in request.POST:
                        user.profession_id = request.POST['profession']
                    if 'cv-clear' in request.POST:
                        user.remove_cv()
                        user.cv = None
                    if 'cv' in request.FILES:
                        user.cv = request.FILES['cv']
                    user.save()
                    if user == request.user:
                        update_session_auth_hash(request, user)
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
        context['title'] = 'Edición del perfil'
        context['action'] = 'edit'
        return context


class UserChooseProfileView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        try:
            group = Group.objects.filter(id=self.kwargs['pk'])
            request.session['group'] = None if not group.exists() else group[0]
        except:
            pass
        finally:
            # success_url = request.session.get('url_current', settings.LOGIN_REDIRECT_URL)
            success_url = settings.LOGIN_REDIRECT_URL
        return HttpResponseRedirect(success_url)


class UserChooseMascotView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        try:
            request.session['pet'] = Mascots.objects.get(id=self.kwargs['pk'])
        except:
            pass
        finally:
            # uccess_url = request.session.get('url_current', settings.LOGIN_REDIRECT_URL)
            success_url = settings.LOGIN_REDIRECT_URL
        return HttpResponseRedirect(success_url)
