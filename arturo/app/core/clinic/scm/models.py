from datetime import datetime

from django.db import models
from django.forms import model_to_dict

from config import settings
from core.clinic.choices import type_product


class Provider(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    ruc = models.CharField(max_length=11, unique=True, verbose_name='Ruc')
    mobile = models.CharField(max_length=10, unique=True, verbose_name='Teléfono celular')
    address = models.CharField(max_length=500, null=True, blank=True, verbose_name='Dirección')
    email = models.CharField(max_length=500, unique=True, verbose_name='Email')

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['-id']


class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name='Nombre')
    desc = models.CharField(max_length=50, verbose_name='Descripción', null=True, blank=True)
    type = models.CharField(choices=type_product, default='vacunas', max_length=30, verbose_name='Categoría')
    image = models.ImageField(upload_to='products/%Y/%m/%d', verbose_name='Imagen', null=True, blank=True)
    price = models.DecimalField(default=0.00, decimal_places=2, max_digits=9, verbose_name='Precio')
    stock = models.IntegerField(default=0)

    def __str__(self):
        return 'Nombre: {} / Precio: ${}'.format(self.name,
                                                 format(self.price, '.2f')
                                                 )

    def get_image(self):
        if self.image:
            return '{}{}'.format(settings.MEDIA_URL, self.image)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def toJSON(self):
        item = model_to_dict(self)
        item['price'] = format(self.price, '.2f')
        item['type'] = {'id': self.type, 'name': self.get_type_display()}
        item['image'] = self.get_image()
        return item

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-id']


class Purchase(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    date_joined = models.DateField(default=datetime.now)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return self.provider.name

    def calculate_invoice(self):
        subtotal = 0.00
        for d in self.detpurchase_set.all():
            subtotal += float(d.price) * int(d.cant)
        self.subtotal = subtotal
        self.save()

    def toJSON(self):
        item = model_to_dict(self)
        item['nro'] = format(self.id, '06d')
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['provider'] = self.provider.toJSON()
        item['subtotal'] = format(self.subtotal, '.2f')
        return item

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        default_permissions = ()
        permissions = (
            ('view_purchase', 'Can view Compras'),
            ('add_purchase', 'Can add Compras'),
            ('delete_purchase', 'Can delete Compras'),
        )
        ordering = ['-id']


class DetPurchase(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cant = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return self.product.name

    def toJSON(self):
        item = model_to_dict(self, exclude=['purchase'])
        item['product'] = self.product.toJSON()
        item['price'] = format(self.price, '.2f')
        item['subtotal'] = format(self.subtotal, '.2f')
        return item

    class Meta:
        verbose_name = 'Det.Compra'
        verbose_name_plural = 'Det.Compras'
        default_permissions = ()
        ordering = ['-id']
