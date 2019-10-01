from django.core.management.base import BaseCommand, CommandError
import django_rq
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from comunitaria.models import Community, UserCommunity
from energy_metering import models

apitoshi_endpoint = "https://57efa5ynx9.execute-api.eu-west-2.amazonaws.com"

def check_statuses():
    unpaid_invoices = models.EnergyInvoice.objects.filter(paid=False)

    for invoice in unpaid_invoices:
        apitoshi_key = invoice.payer.community.communityenergyinfo.apitoshi_apikey
        headers = {'Authorization': 'Bearer %s' % apitoshi_key}

        response = requests.get("%s/prod/payment/%s" % (apitoshi_endpoint,
                                                        invoice.apitoshi_payment_id),
                                 headers=headers)

        if not response.ok:
            print(response.json())  # send to slack incidences
        else:
            status = response.json()['data']['status']
            if status == 'paid':
                invoice.paid = True
                invoice.save()


class Command(BaseCommand):
    help = ('Checks the payment statuses of the unpaid invoices.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            dest='action',
            help='Action to perform (start/stop).',
        )

    def handle(self, *args, **options):
        scheduler = django_rq.get_scheduler('default')
        if options['action'] == 'start':
            job = scheduler.schedule(scheduled_time=timezone.now(),
                                     func=check_statuses,
                                     interval=180)  # Every 180 secs
            print("Job scheduled.")
        else:
            jobs = scheduler.get_jobs()
            for job in jobs:
                if 'check_statuses' in job.func_name:
                    scheduler.cancel(job)
            print("Jobs stopped.")
