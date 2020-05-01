from django.contrib import admin
from .models import HarvestedMouse, HarvestedBasedNumber, HarvestedAdvancedNumber

admin.site.register(HarvestedMouse)
admin.site.register(HarvestedBasedNumber)
admin.site.register(HarvestedAdvancedNumber)
