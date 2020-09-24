from crum import get_current_request
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from core.security.decorators import access_module, get_absolute_path


class AccessModuleMixin(object):

    @method_decorator(login_required)
    @method_decorator(access_module)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class PermissionModuleMixin(object):
    permission_required = None
    url_redirect = reverse_lazy('erp:dashboard')

    def get_perms(self):
        perms = []
        if isinstance(self.permission_required, str):
            perms.append(self.permission_required)
        else:
            perms = list(self.permission_required)
        return perms

    def get_url_redirect(self):
        request = get_current_request()
        group_id = request.user.get_group_id_session()
        url_absolute = get_absolute_path(group_id, request.path)
        if url_absolute != request.path:
            self.url_redirect = url_absolute
        return self.url_redirect

    def dispatch(self, request, *args, **kwargs):
        request = get_current_request()
        # if request.user.is_superuser:
        #     return super().dispatch(request, *args, **kwargs)
        if 'group' in request.session:
            group = request.session['group']
            perms = self.get_perms()
            for p in perms:
                if not group.permissions.filter(codename=p).exists():
                    messages.error(request, 'No tiene permiso para ingresar a este módulo')
                    return HttpResponseRedirect(self.get_url_redirect())
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, 'No tiene permiso para ingresar a este módulo')
        return HttpResponseRedirect(self.get_url_redirect())
