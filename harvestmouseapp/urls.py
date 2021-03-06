from django.urls import path
from harvestmouseapp.views import harvested_mouse_insertion, harvested_mouse_force_list, parsing_imported_mouse, \
    harvested_mouse_get_total_num, clear_all_mouse
from harvestmouseapp.views import harvested_mouse_update
from harvestmouseapp.views import harvested_mouse_delete
from harvestmouseapp.views import harvested_import_mouse
from harvestmouseapp.views import get_data_option_list


urlpatterns = [
    path('insert', harvested_mouse_insertion),
    path('force_list', harvested_mouse_force_list),
    path('list_num', harvested_mouse_get_total_num),
    path('update', harvested_mouse_update),
    path('delete', harvested_mouse_delete),
    path('delete_all', clear_all_mouse),
    path('import', harvested_import_mouse),
    path('getdatalist', get_data_option_list),
    path('parsing_imported_mouse', parsing_imported_mouse)
]
