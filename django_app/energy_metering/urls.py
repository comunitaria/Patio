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

    # EV Central System - Charge Point interaction
    url(r'^messages/?$', api.get_CS_pending_messages, name="get_CS_messages"),
    url(r'^authorize_cp/?$', api.authorize_CP, name="authorize_CP"),
    url(r'^new_transaction/?$', api.new_transaction, name="new_transaction"),
    url(r'^save_cp_energy/?$', api.save_CP_energy_consumption, name="save_cp_energy"),
    url(r'^authorize_user/?$', api.authorize_user, name="authorize_user"),
    url(r'^cp_status_update/?$', api.update_CP_status, name="cp_status_update"),
    
]
