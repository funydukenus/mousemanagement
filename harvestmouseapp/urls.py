from django.urls import path, include
from harvestmouseapp.views import harvested_mouse_insertion, harvested_mouse_force_list, parsing_imported_mouse, \
    gets_mouse_csv_info
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
    path('insert', harvested_mouse_insertion),
    path('list', harvested_mouse_list),
    path('force_list', harvested_mouse_force_list),
    path('update', harvested_mouse_update),
    path('delete', harvested_mouse_delete),
    path('delete/all', harvested_all_mouse_delete),
    path('import', harvested_import_mouse),
    path('getdatalist', get_data_option_list),
    path('parsing_imported_mouse', parsing_imported_mouse),
    path('gets_mouse_csv_info', gets_mouse_csv_info)
]
