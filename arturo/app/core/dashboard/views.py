from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token
from django.views.generic import TemplateView

from core.homepage.models import *
from core.security.models import Dashboard


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'panel.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        request.user.set_group_session()
        data = self.get_context_data()
        dashboard = Dashboard.objects.filter()
        if dashboard.exists():
            if dashboard[0].layout == 1:
                return render(request, 'vtcpanel.html', data)
        return render(request, 'hztpanel.html', data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Panel de administración'
        context['mainpage'] = Mainpage.objects.first()
        context['socialnet'] = SocialNetworks.objects.filter(state=True)
        context['videos'] = Videos.objects.filter(state=True)
        context['news'] = News.objects.filter(state=True)
        return context


@requires_csrf_token
def error_404(request, exception):
    return render(request, '404.html', {})


@requires_csrf_token
def error_500(request, exception):
    return render(request, '500.html', {})
