import json
from io import BytesIO

from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
from django.views.generic.base import View
from xhtml2pdf import pisa

from core.clinic.crm.forms import *
from core.homepage.models import Mainpage
from core.security.mixins import AccessModuleMixin


class DateMedicalClientListView(AccessModuleMixin, FormView):
    template_name = 'datemedical/client/list.html'
    form_class = CrmForm

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'search':
                data = []
                search = DateMedical.objects.filter(client__id=request.user.id)
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                pos = 1
                if len(start_date) and len(end_date):
                    search = search.filter(date_joined__range=[start_date, end_date])
                for d in search.order_by('date_joined', 'hour'):
                    item = d.toJSON()
                    item['pos'] = pos
                    data.append(item)
                    pos += 1
            elif action == 'cancel_cite':
                hist = DateMedical.objects.get(pk=request.POST['id'])
                hist.status = 'cancelado'
                hist.save()
            elif action == 'search_exams':
                data = []
                for i in DateMedicalExam.objects.filter(datemedical_id=request.POST['id']):
                    data.append(i.toJSON())
            elif action == 'search_medicines':
                data = []
                for i in DateMedicalProducts.objects.filter(datemedical_id=request.POST['id']):
                    data.append(i.toJSON())
            elif action == 'search_medicalparameter':
                data = []
                for i in DateMedicalParameters.objects.filter(datemedical_id=request.POST['id']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('datemedical_client_create')
        context['title'] = 'Listado de Citas Médicas'
        return context


class DateMedicalClientCreateView(AccessModuleMixin, FormView):
    template_name = 'datemedical/client/create.html'
    form_class = DateMedicalForm
    success_url = reverse_lazy('datemedical_client_list')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def search_quotes(self):
        data = []
        try:
            date_current = datetime.now()
            date_joined = self.request.POST['date_joined']
            if len(date_joined):
                date_joined = datetime.strptime(date_joined, '%Y-%m-%d')
                pos = 0
                for h in range(8, 19):
                    hour = h
                    if h < 10:
                        hour = '0{}'.format(h)
                    for minute in ['00', '15', '30', '45']:
                        clock = datetime(year=date_joined.year, month=date_joined.month, day=date_joined.day,
                                         hour=int(hour), minute=int(minute))
                        status = 'vacant'
                        hist = DateMedical.objects.filter(date_joined=date_joined,
                                                          hour=clock.time(),
                                                          status='activo')
                        if hist.exists():
                            status = 'reserved'
                        elif date_current > clock:
                            status = 'time_not_available'
                        data.append({
                            'pos': pos,
                            'hour': clock.time().strftime('%H:%M'),
                            'status': status
                        })
                        if h == 18:
                            break
                        pos += 1
        except:
            pass
        return data

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'add':
                with transaction.atomic():
                    datemedical = DateMedical()
                    datemedical.date_joined = datetime.strptime(request.POST['date_joined'], '%Y-%m-%d')
                    datemedical.hour = datetime.strptime(request.POST['hour'], '%H:%M').time()
                    datemedical.client_id = request.user.id
                    datemedical.symptoms = request.POST['symptoms']
                    datemedical.save()
                    msg = 'Cita agendada correctamente para el dia {} a las {}'.format(
                        datemedical.date_joined.strftime('%Y-%m-%d'),
                        datemedical.hour.strftime('%H:%M %p')
                    )
                    data = {'msg': msg}
            elif action == 'search_quotes':
                data = self.search_quotes()
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de una Atención Médica'
        context['action'] = 'add'
        return context


class DateMedicalClientPrintView(View):
    success_url = reverse_lazy('datemedical_client_list')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            template = get_template('datemedical/client/ticket.html')
            context = {
                'comp': Mainpage.objects.first(),
                'datemedical': DateMedical.objects.get(pk=self.kwargs['pk'])
            }
            html = template.render(context)
            result = BytesIO()
            links = lambda uri, rel: os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
            pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result, encoding='UTF-8', link_callback=links)
            return HttpResponse(result.getvalue(), content_type='application/pdf')
        except Exception as e:
            print(e)
        return HttpResponseRedirect(self.success_url)
