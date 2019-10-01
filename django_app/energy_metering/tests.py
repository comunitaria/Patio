from django.test import TestCase
import requests
from rest_framework.test import APIClient
from django.core.management import call_command
import json
from energy_metering.models import ConsumedEnergy
from energy_metering.management.commands.generate_energy_invoices import generate_energy_invoices
import time


class EnergyTest(TestCase):
    fixtures = ['1_comm_2_user.json']

    def test_communities(self):
        client = APIClient()
        response = client.post('/energy/save',
                               {"token": "c78760cf-7716-4045-8d30-186821d9c8f5",
                                "datetime": "2019-09-17 18:49:00+00:00",
                                "amount": "4W",
                                "type": "generated",
                                "mam_address": "mam_addr"
                                })
        self.assertEqual(response.status_code, 200)

        response = client.post('/api-token-auth/',
                               {'username': 'vecino1',
                                'password': 'vecino1'})

        self.assertEqual(response.status_code, 200)

        answer = response.json()
        token = answer['token']
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)

        # Save consumption from neighbour 1
        response = client.post('/energy/save',
                               {"token": "c78760cf-7716-4045-8d30-186821d9c8f5",
                                "datetime": "2019-09-17 19:49:00+00:00",
                                "amount": "1W",
                                "type": "consumed",
                                "mam_address": "mam_addr",
                                "sensor_id": "neighbour_1"
                                })

        self.assertEqual(response.status_code, 200)

        # Save consumption from neighbour 2
        response = client.post('/energy/save',
                               {"token": "c78760cf-7716-4045-8d30-186821d9c8f5",
                                "datetime": "2019-09-17 20:01:00+00:00",
                                "amount": "2W",
                                "type": "consumed",
                                "mam_address": "mam_addr",
                                "sensor_id": "neighbour_2"
                                })

        self.assertEqual(response.status_code, 200)

        # Save consumption from common place
        response = client.post('/energy/save',
                               {"token": "c78760cf-7716-4045-8d30-186821d9c8f5",
                                "datetime": "2019-09-17 19:58:00+00:00",
                                "amount": "3W",
                                "type": "consumed",
                                "mam_address": "mam_addr",
                                "sensor_id": "common_place_1"
                                })

        self.assertEqual(response.status_code, 200)

        # List of generation logs for the community
        response = client.get('/energy/generated/?community=1')

        answer = response.json()
        self.assertTrue(len(answer), 1)

        # List of consumption logs for the usercommunity or common places
        response = client.get('/energy/consumed/?community=1&usercommunity=1')

        answer = response.json()
        self.assertTrue(len(answer), 2)

        # List of consumption logs for the usercommunity or common places
        response = client.get('/energy/consumed/?community=1&usercommunity=2')

        answer = response.json()
        self.assertTrue(len(answer), 2)

        generate_energy_invoices()

        consumption_processed = ConsumedEnergy.objects.filter(processed=True)

        self.assertTrue(len(consumption_processed), 3)

        # List of invoices for the usercommunity
        response = client.get('/energy/invoice/?usercommunity=1')

        answer = response.json()
        self.assertTrue(len(answer), 1)


    def test_2(self):
        pass
