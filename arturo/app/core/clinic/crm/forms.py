from django import forms
from django.forms import ModelForm

from core.clinic.crm.models import *
from core.user.models import Parish

from config import settings


class ExamForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Exam
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese un nombre'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class MedicalParametersForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = MedicalParameters
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese un nombre'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data


class ClientsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parish'].queryset = Parish.objects.none()

    class Meta:
        model = User
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'placeholder': 'Ingrese sus nombres',
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'placeholder': 'Ingrese sus apellidos',
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'username': forms.TextInput(
                attrs={
                    'placeholder': 'Ingrese un username',
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'dni': forms.TextInput(
                attrs={
                    'placeholder': 'Ingrese su número de cedula',
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'email': forms.TextInput(
                attrs={
                    'placeholder': 'Ingrese su correo electrónico',
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'mobile_phone': forms.TextInput(
                attrs={
                    'placeholder': 'Ingrese su número celular',
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'landline': forms.TextInput(
                attrs={
                    'placeholder': 'Ingrese su número fijo',
                    'class': 'form-control',
                    'autocomplete': 'off'
                }
            ),
            'address': forms.TextInput(
                attrs={
                    'placeholder': 'Ingrese una dirección',
                    'class': 'form-control',
                    'autocomplete': 'off',
                }
            ),
            'password': forms.PasswordInput(render_value=True,
                                            attrs={
                                                'placeholder': 'Ingrese un password',
                                                'class': 'form-control',
                                                'autocomplete': 'off'
                                            }
                                            ),
            'gender': forms.Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%',
                'autocomplete': 'off'
            }),
            'birthdate': forms.TextInput(attrs={
                'value': datetime.now().strftime('%Y-%m-%d'),
                'class': 'form-control datetimepicker-input',
                'id': 'birthdate',
                'data-toggle': 'datetimepicker',
                'data-target': '#birthdate'
            }),
            'parish': forms.Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%',
                'autocomplete': 'off'
            }),
        }
        exclude = ['is_change_password', 'is_staff', 'user_permissions', 'date_joined',
                   'last_login', 'is_superuser', 'token' 'groups']

    cv = forms.FileField(widget=forms.FileInput(attrs={
        'class': 'form-control',
    }))


class DateMedicalForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_joined'].widget.attrs['autofocus'] = True
        self.fields['client'].queryset = User.objects.filter(groups__in=[settings.GROUPS.get('client')])

    class Meta:
        model = DateMedical
        fields = '__all__'
        widgets = {
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'placeholder': 'Ingrese una descripción',
                'rows': 4,
                'cols': 4,
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese una descripción',
                'rows': 3,
                'cols': 3,
                'autocomplete': 'off'
            }),
            'treatment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese una descripción',
                'rows': 3,
                'cols': 3,
                'autocomplete': 'off'
            }),
            'client': forms.Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%'
            }),
            'lastperiod_date': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'lastperiod_date',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#lastperiod_date'
            }),
            'date_joined': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'date_joined',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#date_joined'
            }),
            'total': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            }),
            'hour': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'disabled': True,
                'value': '',
            }),
        }


class CrmForm(forms.Form):
    typehistorial = (
        ('', '---------------'),
        ('control_antiparasitario', 'Control Antiparasitario'),
        ('control_vacuna', 'Control de Vacunas'),
    )

    date_range = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off'
    }))

    type_historial = forms.ChoiceField(choices=typehistorial, widget=forms.Select(
        attrs={
            'class': 'form-control select2',
            'style': 'width: 100%'
        }))


class SaleForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = User.objects.none()

    class Meta:
        model = Sale
        fields = '__all__'
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control select2'}),
            'date_joined': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control datetimepicker-input',
                'id': 'date_joined',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'data-toggle': 'datetimepicker',
                'data-target': '#date_joined'
            }),
            'subtotal': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'iva': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            }),
            'total': forms.TextInput(attrs={
                'class': 'form-control',
                'disabled': True
            })
        }
