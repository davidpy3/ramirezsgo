from django.db import models

from django.forms import model_to_dict

from core.clinic.choices import cite_status
from core.clinic.scm.models import Product
from core.user.models import User
from datetime import datetime, timedelta


class Exam(models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=50, unique=True)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Examen'
        verbose_name_plural = 'Exámenes'
        ordering = ['-name']


class MedicalParameters(models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=50, unique=True)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Parametro Medico'
        verbose_name_plural = 'Parametros Medicos'
        ordering = ['-id']


class DateMedical(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    date_joined = models.DateField(default=datetime.now)
    lastperiod_date = models.DateField(default=datetime.now)
    hour = models.TimeField(default=datetime.now)
    symptoms = models.CharField(max_length=5000)
    diagnosis = models.CharField(max_length=5000)
    treatment = models.CharField(max_length=5000)
    status = models.CharField(max_length=15, choices=cite_status, default=cite_status[0][0])
    total = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)

    def __str__(self):
        return self.symptoms

    def get_weekday(self):
        weekday = 0
        lastperiod_date = self.lastperiod_date
        datenow = datetime.now().date()
        while lastperiod_date < datenow:
            if lastperiod_date.weekday() == 6:
                weekday += 1
            lastperiod_date = lastperiod_date + timedelta(days=1)
        return weekday

    def nro(self):
        return format(self.id, '06d')

    def toJSON(self):
        item = model_to_dict(self)
        item['client'] = self.client.toJSON()
        item['date_joined'] = self.date_joined.strftime('%d-%m-%Y')
        item['lastperiod_date'] = self.lastperiod_date.strftime('%d-%m-%Y')
        item['hour'] = self.hour.strftime('%H:%M %p')
        item['status'] = {'id': self.status, 'name': self.get_status_display()}
        item['total'] = format(self.total, '.2f')
        item['weekday'] = self.get_weekday()
        return item

    def calculate_invoice(self):
        subtotal = 0.00
        for d in self.datemedicalproducts_set.all():
            subtotal += float(d.price) * int(d.cant)
        self.total = subtotal + self.total
        self.save()

    class Meta:
        verbose_name = 'Cita Médica'
        verbose_name_plural = 'Citas Médica'
        ordering = ['-id']


class DateMedicalProducts(models.Model):
    datemedical = models.ForeignKey(DateMedical, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cant = models.IntegerField(default=0)
    price = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    subtotal = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)

    def __str__(self):
        return self.product.name

    def toJSON(self):
        item = model_to_dict(self, exclude=['datemedical'])
        item['product'] = self.product.toJSON()
        item['price'] = format(self.price, '.2f')
        item['subtotal'] = format(self.subtotal, '.2f')
        return item

    class Meta:
        verbose_name = 'Cita Médica Producto'
        verbose_name_plural = 'Cita Médica Productos'
        default_permissions = ()
        ordering = ['-id']


class DateMedicalExam(models.Model):
    datemedical = models.ForeignKey(DateMedical, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

    def __str__(self):
        return self.exam.name

    def toJSON(self):
        item = model_to_dict(self, exclude=['datemedical'])
        item['exam'] = self.exam.toJSON()
        return item

    class Meta:
        verbose_name = 'Cita Médica Examen'
        verbose_name_plural = 'Cita Médica Examenes'
        default_permissions = ()
        ordering = ['-id']


class DateMedicalParameters(models.Model):
    datemedical = models.ForeignKey(DateMedical, on_delete=models.CASCADE)
    medicalparameters = models.ForeignKey(MedicalParameters, on_delete=models.CASCADE)
    valor = models.DecimalField(default=0.00, decimal_places=2, max_digits=9)

    def __str__(self):
        return self.medicalparameters.name

    def toJSON(self):
        item = model_to_dict(self, exclude=['datemedical'])
        item['medicalparameters'] = self.medicalparameters.toJSON()
        item['valor'] = format(self.valor, '.2f')
        return item

    class Meta:
        verbose_name = 'Cita Médica Parametro'
        verbose_name_plural = 'Cita Médica Parametros'
        default_permissions = ()
        ordering = ['-id']


class Sale(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date_joined = models.DateField(default=datetime.now)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    iva = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return self.client.get_full_name()

    def nro(self):
        return format(self.id, '06d')

    def toJSON(self):
        item = model_to_dict(self, exclude=[''])
        item['nro'] = format(self.id, '06d')
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['client'] = {} if self.client is None else self.client.toJSON()
        item['subtotal'] = format(self.subtotal, '.2f')
        item['iva'] = format(self.iva, '.2f')
        item['total'] = format(self.total, '.2f')
        return item

    def calculate_invoice(self):
        subtotal = 0.00
        for d in self.detsale_set.all():
            d.subtotal = float(d.price) * int(d.cant)
            d.save()
            subtotal += d.subtotal
        self.subtotal = subtotal
        self.iva = 0.12 * float(self.subtotal)
        self.total = float(self.subtotal) + float(self.iva)
        self.save()

    def delete(self, using=None, keep_parents=False):
        try:
            for i in self.detsale_set.all():
                i.product.stock += i.cant
                i.product.save()
                i.delete()
        except:
            pass
        super(Sale, self).delete()

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        default_permissions = ()
        permissions = (
            ('view_sale', 'Can view Ventas'),
            ('add_sale', 'Can add Ventas'),
            ('delete_sale', 'Can delete Ventas'),
        )
        ordering = ['-id']


class DetSale(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cant = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    dscto = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return self.product.name

    def toJSON(self):
        item = model_to_dict(self, exclude=['sale'])
        item['product'] = self.product.toJSON()
        item['price'] = format(self.price, '.2f')
        item['dscto'] = format(self.dscto, '.2f')
        item['subtotal'] = format(self.subtotal, '.2f')
        return item

    class Meta:
        verbose_name = 'Det. Venta'
        verbose_name_plural = 'Det. Ventas'
        default_permissions = ()
        ordering = ['-id']
