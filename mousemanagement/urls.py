"""mousemanagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from harvestmouseapp.views import harvested_mouse_insertion, harvested_mouse_force_list
from harvestmouseapp.views import harvested_mouse_list
from harvestmouseapp.views import harvested_mouse_update
from harvestmouseapp.views import harvested_mouse_delete
from harvestmouseapp.views import harvested_all_mouse_delete
from harvestmouseapp.views import harvested_import_mouse
from harvestmouseapp.views import get_data_option_list
from usermanagement.views import user_login, user_logout, user_change_password, user_create, create_super_user, \
    is_user_table_empty, hand_checking, is_login, email_test, clear_all_user, create_inactive_user, check_secret_key, \
    user_reset_new_pwd, get_all_user_info

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/harvestedmouse/insert', harvested_mouse_insertion),
    path('api/harvestedmouse/list', harvested_mouse_list),
    path('api/harvestedmouse/force_list', harvested_mouse_force_list),
    path('api/harvestedmouse/update', harvested_mouse_update),
    path('api/harvestedmouse/delete', harvested_mouse_delete),
    path('api/harvestedmouse/delete/all', harvested_all_mouse_delete),
    path('api/harvestedmouse/import', harvested_import_mouse),
    path('api/harvestedmouse/getdatalist', get_data_option_list),
    path('api/accounts/login', user_login),
    path('api/accounts/logout', user_logout),
    path('api/accounts/change_password', user_change_password),
    path('api/accounts/create', create_inactive_user),
    path('api/accounts/create_super_user', create_super_user),
    path('api/accounts/is_user_empty', is_user_table_empty),
    path('api/accounts/islogin', is_login),
    path('api/accounts/sendemail', email_test),
    path('api/accounts/deletealluser', clear_all_user),
    path('api/accounts/checksecretuser', check_secret_key),
    path('api/accounts/newuserpwdchange', user_reset_new_pwd),
    path('api/accounts/getalluserinfo', get_all_user_info),
    path('hc', hand_checking)
]
