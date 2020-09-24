from django.urls import path
from .views.users.views import *
from .views.province.views import *
from .views.parish.views import *
from .views.canton.views import *
from .views.country.views import *

urlpatterns = [
    path('admin/', UserListView.as_view(), name='user_list'),
    path('admin/add/', UserCreateView.as_view(), name='user_create'),
    path('admin/update/<int:pk>/', UserUpdateView.as_view(), name='user_update'),
    path('admin/delete/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),
    path('admin/update/password/', UserUpdatePasswordView.as_view(), name='user_update_password'),
    path('admin/update/profile/', UserUpdateProfileView.as_view(), name='user_update_profile'),
    path('admin/choose/profile/<int:pk>/', UserChooseProfileView.as_view(), name='user_choose_profile'),
    path('admin/choose/mascot/<int:pk>/', UserChooseMascotView.as_view(), name='user_choose_mascot'),
    # province
    path('province/', ProvinceListView.as_view(), name='province_list'),
    path('province/add/', ProvinceCreateView.as_view(), name='province_create'),
    path('province/update/<int:pk>/', ProvinceUpdateView.as_view(), name='province_update'),
    path('province/delete/<int:pk>/', ProvinceDeleteView.as_view(), name='province_delete'),
    # canton
    path('canton/', CantonListView.as_view(), name='canton_list'),
    path('canton/add/', CantonCreateView.as_view(), name='canton_create'),
    path('canton/update/<int:pk>/', CantonUpdateView.as_view(), name='canton_update'),
    path('canton/delete/<int:pk>/', CantonDeleteView.as_view(), name='canton_delete'),
    # parish
    path('parish/', ParishListView.as_view(), name='parish_list'),
    path('parish/add/', ParishCreateView.as_view(), name='parish_create'),
    path('parish/update/<int:pk>/', ParishUpdateView.as_view(), name='parish_update'),
    path('parish/delete/<int:pk>/', ParishDeleteView.as_view(), name='parish_delete'),
    # country
    path('country/', CountryListView.as_view(), name='country_list'),
    path('country/add/', CountryCreateView.as_view(), name='country_create'),
    path('country/update/<int:pk>/', CountryUpdateView.as_view(), name='country_update'),
    path('country/delete/<int:pk>/', CountryDeleteView.as_view(), name='country_delete'),
]
