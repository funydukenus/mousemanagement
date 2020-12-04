from django.urls import path, include
from harvestmouseapp.views import harvested_mouse_insertion, harvested_mouse_force_list, parsing_imported_mouse
from harvestmouseapp.views import harvested_mouse_list
from harvestmouseapp.views import harvested_mouse_update
from harvestmouseapp.views import harvested_mouse_delete
from harvestmouseapp.views import harvested_import_mouse
from harvestmouseapp.views import get_data_option_list


urlpatterns = [
    path('insert', harvested_mouse_insertion),
    path('list', harvested_mouse_list),
    path('force_list', harvested_mouse_force_list),
    path('update', harvested_mouse_update),
    path('delete', harvested_mouse_delete),
    path('import', harvested_import_mouse),
    path('getdatalist', get_data_option_list),
    path('parsing_imported_mouse', parsing_imported_mouse)
]
