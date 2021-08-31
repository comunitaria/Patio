from django.core.management.base import BaseCommand, CommandError
import django_rq
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from comunitaria.models import Community, UserCommunity
from energy_metering import models
import time


def generate_energy_invoices(community_id=None, usercommunity_id=None):
    if not community_id:
        transactions_to_invoice = models.EnergyTransaction.objects.filter(
            invoice=None)
        consumes_to_invoice = models.ConsumedEnergy.objects.filter(
            processed=False)
    else:
        transactions_to_invoice = models.EnergyTransaction.objects.filter(
                                    # Q(producer_community__id=community_id,
                                    # invoice=None) |
                                    Q(consumer_community__id=community_id,
                                    invoice=None)
                                  )

        if usercommunity_id:
            consumes_to_invoice = models.ConsumedEnergy.objects.filter(
                processed=False,
                user_id=usercommunity_id)
        else:
            consumes_to_invoice = models.ConsumedEnergy.objects.filter(
                processed=False,
                community_id=community_id,
                user=None)

    to_invoice = dict()

    # Group consumes by community and user
    for consume in consumes_to_invoice:
        to_invoice.setdefault((consume.community, consume.user), [])
        to_invoice[(consume.community, consume.user)].append(consume)

    for etransaction in transactions_to_invoice:
        to_invoice.setdefault((etransaction.producer_community,
                               etransaction.consumer_community),
                               [])
        to_invoice[(etransaction.producer_community,
                    etransaction.consumer_community)].append(etransaction)

    # Create invoices
    for k, v in to_invoice.items():
        producer, consumer = k
        concept = ("Energy invoice from Community %s" %
                   producer.community_address)
        total = sum([elem.price for elem in v])

        # To be filled with payment request ID from invoicing systems
        pay_req = ""

        invoice = models.EnergyInvoice(concept=concept,
                                       total=total,
                                       payment_req=pay_req)

        if type(consumer) is Community:
            # Assign the invoice to the consumer community administrator
            payer = consumer.users.filter(administrator=True).first()
        elif consumer is None:
            # Assign invoice to producer community administrator
            # (it was autoconsume from common places)
            payer = producer.users.filter(administrator=True).first()
        else:
            # Consumer is user (neighbour) from producer community
            payer = consumer

        invoice.payer = payer
        invoice.save()

        for elem in v:
            elem.invoice = invoice
            if hasattr(elem, 'processed'):
                elem.processed = True
            elem.save()


class Command(BaseCommand):
    help = ('Gets not invoiced Consumes and Energy Transactions between '
            'communities.')

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
                                     func=generate_energy_invoices,
                                     interval=30)  # Every 30 secs
            print("Job scheduled.")
        else:
            jobs = scheduler.get_jobs()
            for job in jobs:
                if 'generate_energy_invoices' in job.func_name:
                    scheduler.cancel(job)
            print("Jobs stopped.")
