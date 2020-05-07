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
from harvestmouseapp.views import harvested_mouse_insertion
from harvestmouseapp.views import harvested_mouse_list
from harvestmouseapp.views import harvested_mouse_update
from harvestmouseapp.views import harvested_mouse_delete
from harvestmouseapp.views import harvested_all_mouse_delete
from harvestmouseapp.views import harvested_import_mouse

urlpatterns = [
    path('admin/', admin.site.urls),
    path('harvestedmouse/insert', harvested_mouse_insertion),
    path('harvestedmouse/list', harvested_mouse_list),
    path('harvestedmouse/update', harvested_mouse_update),
    path('harvestedmouse/delete', harvested_mouse_delete),
    path('harvestedmouse/delete/all', harvested_all_mouse_delete),
    path('harvestedmouse/import', harvested_import_mouse),
]
