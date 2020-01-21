from django.contrib import admin
from .models import *

admin.site.register(GeneratedEnergy)
admin.site.register(ConsumedEnergy)
admin.site.register(EnergyTransaction)
admin.site.register(EnergyInvoice)
admin.site.register(CommunityEnergyInfo)
admin.site.register(CentralSystem)
admin.site.register(ChargePoint)
admin.site.register(EVTransaction)
admin.site.register(CPMessage)
