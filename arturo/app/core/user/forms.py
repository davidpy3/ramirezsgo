from django import forms
from django.forms import ModelForm

from core.user.models import *


class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['groups'].required = True
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
                    'placeholder': 'Ingrese su número de cedula',
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
            'groups': forms.SelectMultiple(attrs={
                'class': 'select2',
                'multiple': 'multiple',
                'style': 'width:100%'
            }),
        }
        exclude = ['is_change_password', 'is_staff', 'user_permissions', 'date_joined',
                   'last_login', 'is_superuser', 'token']


class ProfileForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['autofocus'] = True

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
                    'placeholder': 'Ingrese su número de cedula',
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
            'profession': forms.Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%',
                'autocomplete': 'off'
            }),
        }
        exclude = ['is_change_password', 'is_staff', 'user_permissions', 'date_joined',
                   'last_login', 'is_superuser', 'token', 'groups', 'is_active']

    token = forms.CharField(widget=forms.HiddenInput(), required=False)


class CountryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Country
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


class ProvinceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Province
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese un nombre'}),
            'code': forms.TextInput(attrs={'placeholder': 'Ingrese un código'}),
            'country': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
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


class CantonForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Canton
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese un nombre'}),
            'province': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
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


class ParishForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Parish
        fields = 'canton', 'name'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingrese un nombre'}),
            'canton': forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'}),
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
