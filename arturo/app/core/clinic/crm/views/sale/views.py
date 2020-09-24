import json
import os
from io import BytesIO

from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.http import JsonResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, CreateView, DeleteView, View
from xhtml2pdf import pisa

from core.clinic.crm.forms import *
from core.clinic.scm.models import Product
from core.homepage.models import Mainpage
from core.reports.forms import ReportForm
from core.security.mixins import AccessModuleMixin, PermissionModuleMixin


class SaleListView(AccessModuleMixin, PermissionModuleMixin, FormView):
    template_name = 'sale/list.html'
    permission_required = 'view_sale'
    form_class = ReportForm

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        action = request.POST.get('action', None)
        try:
            if action == 'search':
                data = []
                start_date = request.POST['start_date']
                end_date = request.POST['start_date']
                search = Sale.objects.filter()
                if len(start_date) and len(end_date):
                    search = search.filter(date_joined__range=[start_date, end_date])
                for i in search:
                    data.append(i.toJSON())
            elif action == 'search_detproducts':
                data = []
                for det in DetSale.objects.filter(sale_id=request.POST['id']):
                    data.append(det.toJSON())
            else:
                data['error'] = 'No ha ingresado una opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('sale_create')
        context['title'] = 'Listado de Ventas'
        return context


class SaleCreateView(AccessModuleMixin, PermissionModuleMixin, CreateView):
    model = Sale
    template_name = 'sale/create.html'
    form_class = SaleForm
    success_url = reverse_lazy('sale_list')
    permission_required = 'add_sale'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def validate_client(self):
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

    def get_form_client(self):
        form = ClientsForm()
        del form.fields['password']
        del form.fields['groups']
        del form.fields['cv']
        del form.fields['is_active']
        return form

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', None)
        data = {}
        try:
            if action == 'add':
                with transaction.atomic():
                    items = json.loads(request.POST['items'])
                    vent = Sale()
                    vent.client_id = items['client']
                    vent.date_joined = items['date_joined']
                    vent.save()

                    for i in items['products']:
                        det = DetSale()
                        det.sale_id = vent.id
                        det.product_id = i['id']
                        det.cant = int(i['cant'])
                        det.price = float(i['price'])
                        det.total = det.cant * float(det.price)
                        det.save()

                        det.product.stock -= det.cant
                        det.product.save()

                    vent.calculate_invoice()

                    data = {'id': vent.id}
            elif action == 'search_products':
                ids = json.loads(request.POST['ids'])
                data = []
                term = request.POST['term']
                search = Product.objects.filter(stock__gt=0).exclude(id__in=ids).order_by('name')
                if len(term):
                    search = search.filter(name__icontains=term)
                    search = search[:10]
                for p in search:
                    if p.stock > 0:
                        item = p.toJSON()
                        item['value'] = '{} / {} / {}'.format(p.name, p.get_type_display(), p.stock)
                        data.append(item)
            elif action == 'search_client':
                data = []
                term = request.POST['term']
                for i in User.objects.filter(groups__in=[settings.GROUPS.get('client')]).filter(
                        Q(first_name__icontains=term) | Q(last_name__icontains=term) | Q(
                            dni__icontains=term))[0:10]:
                    item = {'id': i.id, 'text': '{}/{}'.format(i.get_full_name(), i.dni), 'data': i.toJSON()}
                    data.append(item)
            elif action == 'validate_client':
                return self.validate_client()
            elif action == 'create_client':
                with transaction.atomic():
                    user = User()
                    user.first_name = request.POST['first_name']
                    user.last_name = request.POST['last_name']
                    user.dni = request.POST['dni']
                    if 'image' in request.FILES:
                        user.image = request.FILES['image']
                    user.create_or_update_password(user.dni)
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
            elif action == 'search_parish':
                data = []
                term = request.POST['term']
                for i in Parish.objects.filter(name__icontains=term)[0:10]:
                    name = 'Pais: {} / Provincia: {} / Cantón: {} / Parroquia: {}'.format(
                        i.canton.province.country.name, i.canton.province.name, i.canton.name, i.name)
                    item = {'id': i.id, 'text': name, 'data': i.toJSON()}
                    data.append(item)
            else:
                data['error'] = 'No ha ingresado una opción'
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['frmClient'] = self.get_form_client()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de una Venta'
        context['action'] = 'add'
        return context


class SaleDeleteView(AccessModuleMixin, PermissionModuleMixin, DeleteView):
    model = Sale
    template_name = 'sale/delete.html'
    success_url = reverse_lazy('sale_list')
    permission_required = 'delete_sale'

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


class SalePrintInvoice(View):
    success_url = reverse_lazy('sale_list')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            template = get_template('sale/invoice.html')
            context = {
                'comp': Mainpage.objects.first(),
                'sale': Sale.objects.get(pk=self.kwargs['pk'])
            }
            html = template.render(context)
            result = BytesIO()
            links = lambda uri, rel: os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
            pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result, encoding='UTF-8', link_callback=links)
            return HttpResponse(result.getvalue(), content_type='application/pdf')
        except Exception as e:
            print(e)
        return HttpResponseRedirect(self.success_url)
