import json
import os
from io import BytesIO

from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView, DeleteView, FormView
from django.views.generic.base import View
from xhtml2pdf import pisa

from core.clinic.crm.forms import *
from core.homepage.models import Mainpage
from core.security.mixins import AccessModuleMixin


class DateMedicalAdminListView(AccessModuleMixin, FormView):
    template_name = 'datemedical/admin/list.html'
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
                search = DateMedical.objects.filter()
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
        context['title'] = 'Listado de Citas Médicas'
        context['create_url'] = reverse_lazy('datemedical_admin_create')
        return context


class DateMedicalAdminCreateView(AccessModuleMixin, FormView):
    model = DateMedical
    template_name = 'datemedical/admin/create.html'
    form_class = DateMedicalForm
    success_url = reverse_lazy('datemedical_admin_list')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'add':
                with transaction.atomic():
                    datemedical = DateMedical()
                    datemedical.client_id = request.POST['client']
                    datemedical.symptoms = request.POST['symptoms']
                    datemedical.lastperiod_date = request.POST['lastperiod_date']
                    datemedical.date_joined = request.POST['date_joined']
                    datemedical.treatment = request.POST['treatment']
                    datemedical.diagnosis = request.POST['diagnosis']
                    datemedical.status = 'finalizado'
                    datemedical.total = float(request.POST['total'])
                    datemedical.save()

                    for p in json.loads(request.POST['medicines']):
                        det = DateMedicalProducts()
                        det.datemedical_id = datemedical.id
                        det.product_id = p['id']
                        det.price = float(p['price'])
                        det.cant = int(p['cant'])
                        det.subtotal = det.price * det.cant
                        det.save()
                        det.product.stock -= det.cant
                        det.product.save()

                    for exa in json.loads(request.POST['exams']):
                        det = DateMedicalExam()
                        det.datemedical_id = datemedical.id
                        det.exam_id = exa['id']
                        det.save()

                    for med in json.loads(request.POST['medicalparameters']):
                        det = DateMedicalParameters()
                        det.datemedical_id = datemedical.id
                        det.medicalparameters_id = med['id']
                        det.valor = float(med['valor'])
                        det.save()

                    datemedical.calculate_invoice()
            elif action == 'get_parameters':
                data = []
                for p in MedicalParameters.objects.filter():
                    item = p.toJSON()
                    item['valor'] = '0.00'
                    data.append(item)
            elif action == 'search_medicine':
                data = []
                term = request.POST['term']
                ids = json.loads(request.POST['ids'])
                products = Product.objects.filter(name__icontains=term, type__in=['medicamentos', 'vacunas']).exclude(
                    id__in=ids)[0:10]
                pos = 1
                for i in products:
                    if i.stock > 0:
                        item = i.toJSON()
                        item['pos'] = pos
                        prod = {'id': i.id, 'text': i.__str__(), 'data': item}
                        data.append(prod)
                        pos += 1
            elif action == 'get_exams':
                data = []
                for p in Exam.objects.filter():
                    item = p.toJSON()
                    item['state'] = 0
                    data.append(item)
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Registro de una cita médica'
        context['action'] = 'add'
        return context


class DateMedicalAdminUpdateView(AccessModuleMixin, UpdateView):
    model = DateMedical
    template_name = 'datemedical/admin/attend.html'
    form_class = DateMedicalForm
    success_url = reverse_lazy('datemedical_admin_list')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'add':
                with transaction.atomic():
                    datemedical = self.object
                    datemedical.lastperiod_date = request.POST['lastperiod_date']
                    datemedical.treatment = request.POST['treatment']
                    datemedical.diagnosis = request.POST['diagnosis']
                    datemedical.status = 'finalizado'
                    datemedical.total = float(request.POST['total'])
                    datemedical.save()

                    for p in json.loads(request.POST['medicines']):
                        det = DateMedicalProducts()
                        det.datemedical_id = datemedical.id
                        det.product_id = p['id']
                        det.price = float(p['price'])
                        det.cant = int(p['cant'])
                        det.subtotal = det.price * det.cant
                        det.save()
                        det.product.stock -= det.cant
                        det.product.save()

                    for exa in json.loads(request.POST['exams']):
                        det = DateMedicalExam()
                        det.datemedical_id = datemedical.id
                        det.exam_id = exa['id']
                        det.save()

                    for med in json.loads(request.POST['medicalparameters']):
                        det = DateMedicalParameters()
                        det.datemedical_id = datemedical.id
                        det.medicalparameters_id = med['id']
                        det.valor = float(med['valor'])
                        det.save()

                    datemedical.calculate_invoice()
            elif action == 'get_parameters':
                data = []
                for p in MedicalParameters.objects.filter():
                    item = p.toJSON()
                    item['valor'] = '0.00'
                    data.append(item)
            elif action == 'search_medicine':
                data = []
                term = request.POST['term']
                ids = json.loads(request.POST['ids'])
                products = Product.objects.filter(name__icontains=term, type__in=['medicamentos', 'vacunas']).exclude(
                    id__in=ids)[0:10]
                pos = 1
                for i in products:
                    if i.stock > 0:
                        item = i.toJSON()
                        item['pos'] = pos
                        prod = {'id': i.id, 'text': i.__str__(), 'data': item}
                        data.append(prod)
                        pos += 1
            elif action == 'get_exams':
                data = []
                for p in Exam.objects.filter():
                    item = p.toJSON()
                    item['state'] = 0
                    data.append(item)
            else:
                data['error'] = 'No ha seleccionado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['list_url'] = self.success_url
        context['title'] = 'Atención de una cita médica'
        context['action'] = 'add'
        context['instance'] = self.object
        return context


class DateMedicalAdminDeleteView(AccessModuleMixin, DeleteView):
    model = DateMedical
    template_name = 'datemedical/admin/delete.html'
    success_url = reverse_lazy('datemedical_admin_list')

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


class DateMedicalAdminPrintView(View):
    success_url = reverse_lazy('datemedical_admin_list')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            template = get_template('datemedical/admin/ticket.html')
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
