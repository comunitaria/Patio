from . import api
from django.conf.urls import include, url
from rest_framework import routers

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'generated', api.GeneratedEnergyViewSet)
router.register(r'consumed', api.ConsumedEnergyViewSet)
router.register(r'invoice', api.EnergyInvoiceViewSet)
router.register(r'transaction', api.EnergyTransactionViewSet)

urlpatterns = [
    url(r'^save/?$', api.save_energy_action, name="save_energy_action"),
    url(r'^manual_invoice/?$', api.manual_invoice_generation,
        name="manual_invoice_generation"),
    url(r'', include(router.urls)),
]
