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
        # UserCommunity 2 is also administrator
        response = client.get('/energy/consumed/?community=1&usercommunity=2')

        answer = response.json()
        self.assertTrue(len(answer), 3)

        response = client.get('/energy/manual_invoice/?community=1&usercommunity=1')

        time.sleep(2)
        consumption_processed = ConsumedEnergy.objects.filter(processed=True)
        self.assertTrue(len(consumption_processed), 1)

        # List of invoices for the usercommunity 1
        response = client.get('/energy/invoice/?usercommunity=1')

        answer = response.json()
        self.assertTrue(len(answer), 1)

        # List invoices for user 2
        response = client.get('/energy/invoice/?usercommunity=2')
        answer = response.json()

        # 1 invoice (user 2 (admin) can see user 1's invoice)
        self.assertTrue(len(answer), 1)

        # Gen invoices for user 2
        response = client.get('/energy/manual_invoice/?community=1&usercommunity=2')

        consumption_processed = ConsumedEnergy.objects.filter(processed=True)
        self.assertTrue(len(consumption_processed), 3)

        # List of invoices for the usercommunity 2 (neighbor and administrator)
        response = client.get('/energy/invoice/?usercommunity=2')

        answer = response.json()
        # 2 invoices (user 1, and administrator (common place and user 2))
        self.assertTrue(len(answer), 2)


    def test_2(self):
        pass


class EVEnergyTest(TestCase):
    fixtures = ['1_comm_2_user_1cs_1cp.json']

    def test_authorize_cp(self):
        """
            BootNotification
        """
        client = APIClient()
        response = client.post('/energy/authorize_cp',
                               {"token": "8fb259bb-6b73-4357-a840-8a0048de0af3",
                                "cp_id": "serial123"
                                })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

    def test_save_cp_energy(self):
        """
            StartTransaction
            StopTransaction
        """
        client = APIClient()

        response = client.post('/energy/new_transaction',
                               {"token": "8fb259bb-6b73-4357-a840-8a0048de0af3",
                                "user_id": "1"
                                })
        self.assertEqual(response.status_code, 200)

        answer = response.json()
        self.assertEqual(answer['status'], 'ok')
        transaction_id = answer['transaction_id']

        response = client.post('/energy/authorize_cp',
                               {"token": "8fb259bb-6b73-4357-a840-8a0048de0af3",
                                "cp_id": "serial123",
                                "datetime": "2019-09-17 19:49:00+00:00",
                                "amount": "10",
                                "mam_address": "",
                                "transaction_id": transaction_id
                                })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')


    def test_authorize_user(self):
        """
            Authorize
        """
        client = APIClient()

        response = client.post('/energy/authorize_user',
                               {"token": "8fb259bb-6b73-4357-a840-8a0048de0af3",
                                "user_id": "1",
                                "cp_id": "serial123"
                                })
        self.assertEqual(response.status_code, 200)

        answer = response.json()
        self.assertEqual(answer['status'], 'ok')

        response = client.post('/energy/authorize_user',
                               {"token": "8fb259bb-6b73-4357-a840-8a0048de0af3",
                                "user_id": "2",
                                "cp_id": "serial123"
                                })
        self.assertEqual(response.status_code, 200)

        answer = response.json()
        self.assertEqual(answer['status'], 'nok')


    def test_cp_status_update(self):
        """
            StatusNotification
        """
        client = APIClient()

        response = client.post('/energy/cp_status_update',
                               {"token": "8fb259bb-6b73-4357-a840-8a0048de0af3",
                                "status": "Charging",
                                "cp_id": "serial123",
                                "error_code": "noerror",
                                "connector_id": 1
                                })
        self.assertEqual(response.status_code, 200)

        answer = response.json()
        self.assertEqual(answer['status'], 'ok')


    def test_get_messages(self):
        """
            Get messages fot the given CP
        """
        client = APIClient()

        response = client.get('/energy/messages',
                               {"token": "8fb259bb-6b73-4357-a840-8a0048de0af3",
                                "cp_id": "serial123",
                                })
        self.assertEqual(response.status_code, 200)

        answer = response.json()
        self.assertEqual(answer['status'], 'ok')
        print(answer['messages'])
