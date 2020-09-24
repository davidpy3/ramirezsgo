import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.contrib.auth.models import Group
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, UpdateView, FormView

from core.clinic.crm.forms import ClientsForm, User, Parish, Product
from core.homepage.forms import *
from core.homepage.models import SocialNetworks
from core.security.mixins import AccessModuleMixin, PermissionModuleMixin


class MainPageIndexView(TemplateView):
    template_name = 'mainpage/index.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'send_comments':
                com = Comments()
                com.names = request.POST['names']
                com.email = request.POST['email']
                com.mobile = request.POST['mobile']
                com.message = request.POST['message']
                com.save()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Pagina principal'
        context['mainpage'] = Mainpage.objects.first()
        context['socialnetworks'] = SocialNetworks.objects.filter(state=True)
        context['statistics'] = Statistics.objects.filter(state=True).order_by('name')
        context['services'] = Services.objects.filter(state=True).order_by('id').order_by('name')
        context['departments'] = Departments.objects.filter(state=True).order_by('id').order_by('name')
        context['feqQuestions'] = FreqQuestions.objects.filter(state=True).order_by('id')
        context['testimonials'] = Testimonials.objects.filter(state=True).order_by('id')
        context['gallery'] = Gallery.objects.filter(state=True).order_by('id')
        context['team'] = Team.objects.filter(state=True).order_by('id')
        context['qualities'] = Qualities.objects.filter(state=True).order_by('id')
        context['products'] = Product.objects.filter().order_by('id')
        context['form'] = CommentsForm()
        return context


class MainPageUpdateView(AccessModuleMixin, PermissionModuleMixin, UpdateView):
    template_name = 'mainpage/create.html'
    permission_required = 'view_mainpage'
    form_class = MainpageForm

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        mainpage = Mainpage.objects.all()
        if mainpage.exists():
            return mainpage[0]
        return Mainpage()

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'edit':
                mainpage = self.get_object()
                mainpage.name = request.POST['name']
                mainpage.proprietor = request.POST['proprietor']
                mainpage.desc = request.POST['desc']
                mainpage.with_us = request.POST['with_us']
                mainpage.mission = request.POST['mission']
                mainpage.vision = request.POST['vision']
                mainpage.about_us = request.POST['about_us']
                mainpage.mobile = request.POST['mobile']
                mainpage.phone = request.POST['phone']
                mainpage.email = request.POST['email']
                mainpage.address = request.POST['address']
                mainpage.horary = request.POST['horary']
                mainpage.coordinates = request.POST['coordinates']
                mainpage.about_youtube = request.POST['about_youtube']
                if 'icon_image' in request.FILES:
                    mainpage.icon_image = request.FILES['icon_image']
                mainpage.save()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Configuración de la página principal'
        context['action'] = 'edit'
        return context


class SignInView(FormView):
    form_class = ClientsForm
    template_name = 'mainpage/sign_in.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def validate_data(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            obj = self.request.POST['obj'].strip()
            if type == 'dni':
                if User.objects.filter(dni=obj):
                    data['valid'] = False
        except:
            pass
        return JsonResponse(data)

    def send_email(self, id):
        url = settings.LOCALHOST if not settings.DEBUG else self.request.META['HTTP_HOST']
        user = User.objects.get(pk=id)
        message = MIMEMultipart('alternative')
        message['Subject'] = 'Registro de cuenta'
        message['From'] = settings.EMAIL_HOST_USER
        message['To'] = user.email

        parameters = {
            'user': user,
            'mainpage': Mainpage.objects.first(),
            'link_home': 'http://{}'.format(url),
            'link_login': 'http://{}/login'.format(url)
        }

        html = render_to_string('mainpage/email_sign_in.html', parameters)
        content = MIMEText(html, 'html')
        message.attach(content)
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.sendmail(
            settings.EMAIL_HOST_USER, user.email, message.as_string()
        )
        server.quit()

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

                    group = Group.objects.get(pk=settings.GROUPS.get('client'))
                    user.groups.add(group)

                    self.send_email(user.id)
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
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registro de un cliente'
        return context
