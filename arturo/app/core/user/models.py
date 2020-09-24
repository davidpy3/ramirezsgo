# -*- codign: utf-8 -*-
import os
import uuid
from datetime import datetime

from crum import get_current_request
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import AbstractUser, Group, UserManager
from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone

from config import settings
from core.user.choices import gender_person


class Country(models.Model):
    code = models.CharField(max_length=4, verbose_name='Código', unique=True)
    name = models.CharField(max_length=50, verbose_name='Nombre', unique=True)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'País'
        verbose_name_plural = 'Paises'
        ordering = ['-id']


class Province(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='País')
    name = models.CharField(max_length=50, verbose_name='Nombre', unique=True)
    code = models.CharField(max_length=4, verbose_name='Código', unique=True)

    def __str__(self):
        return 'País: {} / Provincia: {}'.format(self.country.name, self.name)

    def toJSON(self):
        item = model_to_dict(self)
        item['country'] = self.country.toJSON()
        return item

    class Meta:
        verbose_name = 'Provincia'
        verbose_name_plural = 'Provincias'
        ordering = ['-id']


class Canton(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE, verbose_name='Provincia')
    name = models.CharField(max_length=50, verbose_name='Nombre')

    def __str__(self):
        return '{} / Cantón: {}'.format(self.province.__str__(), self.name)

    def toJSON(self):
        item = model_to_dict(self)
        item['province'] = self.province.toJSON()
        return item

    class Meta:
        verbose_name = 'Cantón'
        verbose_name_plural = 'Cantones'
        ordering = ['-id']


class Parish(models.Model):
    canton = models.ForeignKey(Canton, on_delete=models.CASCADE, verbose_name='Cantón')
    name = models.CharField(max_length=50, verbose_name='Nombre')

    def __str__(self):
        return '{} / Parroquia: {}'.format(self.canton.__str__(), self.name)

    def toJSON(self):
        item = model_to_dict(self)
        item['canton'] = self.canton.toJSON()
        return item

    class Meta:
        verbose_name = 'Parroquia'
        verbose_name_plural = 'Parroquias'
        ordering = ['-id']


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100, verbose_name='Nombres')
    last_name = models.CharField(max_length=100, verbose_name='Apellidos')
    email = models.CharField(max_length=50, verbose_name='Email', unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    dni = models.CharField(max_length=8, unique=True, verbose_name='Número de cedula')
    image = models.ImageField(upload_to='users/%Y/%m/%d', null=True, blank=True, verbose_name='Imagen')
    gender = models.CharField(max_length=10, choices=gender_person, default=gender_person[0][0], verbose_name='Sexo')
    mobile_phone = models.CharField(max_length=9, unique=True, verbose_name='Teléfono celular')
    landline = models.CharField(max_length=6, unique=True, verbose_name='Teléfono convencional')
    address = models.CharField(max_length=500, null=True, blank=True, verbose_name='Dirección')
    birthdate = models.DateField(default=datetime.now, verbose_name='Fecha de nacimiento')
    parish = models.ForeignKey(Parish, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Parroquia')
    cv = models.FileField(upload_to='cv/%Y/%m/%d', null=True, blank=True)
    is_change_password = models.BooleanField(default=False)
    token = models.UUIDField(primary_key=False, editable=False, null=True, blank=True, default=uuid.uuid4, unique=True)
    objects = UserManager()
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'dni'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        full_name = '{} {}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def get_cv(self):
        if self.cv:
            return '{}{}'.format(settings.MEDIA_URL, self.cv)
        return ''

    def remove_cv(self):
        try:
            if self.cv:
                os.remove(self.cv.path)
        except:
            pass

    def toJSON(self):
        item = model_to_dict(self, exclude=['last_login', 'token', 'password', 'user_permissions', 'parish'])
        item['image'] = self.get_image()
        item['full_name'] = self.get_full_name()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['groups'] = [{'id': i.id, 'name': i.name} for i in self.groups.all()]
        if self.last_login:
            item['last_login'] = self.last_login.strftime('%Y-%m-%d')
        item['gender'] = {'id': self.gender, 'name': self.get_gender_display()}
        item['parish'] = {} if self.parish is None else self.parish.toJSON()
        item['birthdate'] = self.birthdate.strftime('%Y-%m-%d')
        item['cv'] = self.get_cv()
        return item

    def generate_token(self):
        return uuid.uuid4()

    def get_access_users(self):
        data = []
        for i in self.accessusers_set.all():
            data.append(i.toJSON())
        return data

    def get_image(self):
        if self.image:
            return '{}{}'.format(settings.MEDIA_URL, self.image)
        return '{}{}'.format(settings.STATIC_URL, 'img/default/empty.png')

    def remove_image(self):
        try:
            if self.image:
                os.remove(self.image.path)
        except:
            pass

    def delete(self, using=None, keep_parents=False):
        try:
            os.remove(self.image.path)
        except:
            pass
        super(User, self).delete()

    def get_groups(self):
        data = []
        for i in self.groups.all():
            data.append({'id': i.id, 'name': i.name})
        return data

    def get_group_id_session(self):
        try:
            request = get_current_request()
            return int(request.session['group'].id)
        except:
            return 0

    def set_group_session(self):
        try:
            request = get_current_request()
            groups = request.user.groups.all()
            if groups:
                if 'group' not in request.session:
                    request.session['group'] = groups[0]
                pets = self.get_pets()
                if len(pets):
                    if 'pet' not in request.session:
                        request.session['pet'] = pets[0]
        except:
            pass

    def is_employee(self):
        try:
            request = get_current_request()
            if 'group' in request.session:
                return request.session['group'].id == settings.GROUPS.get('employee')
        except:
            pass
        return False

    def create_or_update_password(self, password):
        try:
            if self.pk is None:
                self.set_password(password)
            else:
                user = User.objects.get(pk=self.pk)
                if user.password != password:
                    self.set_password(password)
        except:
            pass

    def get_pets(self):
        mascots = []
        try:
            mascots = self.mascots_set.all()
        except:
            pass
        return mascots

    def __str__(self):
        full_name = self.get_full_name()
        if self.groups.filter(id=settings.GROUPS.get('employee')):
            if self.profession:
                return '{} / {}'.format(full_name, self.profession.name)
        return full_name

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-id']
