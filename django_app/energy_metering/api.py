from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from . import serializers
from comunitaria.models import UserCommunity
from comunitaria.utils import check_user_comm_permissions
from energy_metering.management.commands.generate_energy_invoices import generate_energy_invoices
from .models import (GeneratedEnergy, ConsumedEnergy, EnergyTransaction,
                     EnergyInvoice, CommunityEnergyInfo, CentralSystem,
                     ChargePoint, CPConnector, CPMessage, EVTransaction)


power_unit = 'W'


def get_community_from_token(token):
    community_info = CommunityEnergyInfo.objects.filter(token=token).first()

    return community_info


@api_view(['POST'])
@permission_classes((AllowAny, ))
def save_energy_action(request):
    """
        Receives data representing a generation or consumption action
        from a Patio device.
    """
    params = request.data
    token = params['token']
    date = params['datetime']
    amount = params['amount']
    e_type = params['type']
    dlt_address = params['dlt_address']
    sensor_id = params.get('sensor_id', '')

    amount = amount.replace(power_unit, '').strip()

    community_info = get_community_from_token(token)
    if not community_info:
        return Response({'status': 'nok', 'msg': 'Invalid token'})

    if e_type == 'generated':
        # Look if log already exists
        generated_log_exists = GeneratedEnergy.objects.filter(
            community=community_info.community,
            energy_amount=amount,
            time=date)
        if generated_log_exists:
            return Response({'status': 'duplicated'})

        gen_obj = GeneratedEnergy(community=community_info.community,
                                  energy_amount=amount,
                                  time=date,
                                  dlt_address=dlt_address)
        gen_obj.save()
    else:
        unit_price = community_info.in_community_energy_price

        # unit_price (W/h) divided by 3600 seconds and multiplied by 
        # 5 (size of the interval we chose to send data from Patio device)
        price = (float(unit_price)/3600) * 5 * float(amount)
        user_comm = None

        # If the consumption belongs to a specific neighbour instead of
        # common places
        if 'neighbour' in sensor_id:
            user_comm_id = sensor_id.split('_')[1]
            user_comm = community_info.community.users.filter(id=user_comm_id).first()

        # Look if log already exists
        consume_log_exists = ConsumedEnergy.objects.filter(
            community=community_info.community,
            energy_amount=amount,
            time=date)
        if consume_log_exists:
            return Response({'status': 'duplicated'})

        consume_obj = ConsumedEnergy(community=community_info.community,
                                     energy_amount=amount,
                                     time=date,
                                     dlt_address=dlt_address,
                                     price=price,
                                     user=user_comm)
        consume_obj.save()

    return Response({'status': 'ok'})


@api_view(['POST'])
def get_pending_messages(request):
    """
        Returns pending messages for a community's Patio device.
        Messages can be informative, or related to any sensor, ...
    """

    # TODO

    return Response({'status': 'ok'})


@api_view(['GET'])
def manual_invoice_generation(request):
    """
        Query parameter community and usercommunity are expected
        /energy/manual_invoice/?community=1&usercommunity=1
    """
    community_id = request.query_params.get('community', None)
    usercomm_id = request.query_params.get('usercommunity', None)
    allowed, response = check_user_comm_permissions(request, community_id)

    if not allowed:
        return Response({'status': 'error'})

    usercomm = UserCommunity.objects.filter(id=usercomm_id).first()
    generate_energy_invoices(community_id=community_id,
                             usercommunity_id=usercomm_id)

    if usercomm.administrator:
        generate_energy_invoices(community_id=community_id,
                                 usercommunity_id=None)

    return Response({'status': 'ok'})


class GeneratedEnergyViewSet(viewsets.ReadOnlyModelViewSet):
    """
        GeneratedEnergy
        Query parameter 'community' is expected
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.GeneratedEnergySerializer
    queryset = GeneratedEnergy.objects.all()

    def get_queryset(self):
        community_id = self.request.query_params.get('community', None)
        allowed, response = check_user_comm_permissions(self.request,
                                                        community_id)
        if not allowed:
            return GeneratedEnergy.objects.none()

        return GeneratedEnergy.objects.filter(community__id=community_id)


class ConsumedEnergyViewSet(viewsets.ReadOnlyModelViewSet):
    """
        ConsumedEnergy
        Query parameter community and usercommunity are expected
        /energy/consumed/?community=1&usercommunity=1
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ConsumedEnergySerializer
    queryset = ConsumedEnergy.objects.all()

    def get_queryset(self):
        community_id = self.request.query_params.get('community', None)
        usercomm_id = self.request.query_params.get('usercommunity', None)
        allowed, response = check_user_comm_permissions(self.request,
                                                        community_id)

        usercomm = UserCommunity.objects.filter(id=usercomm_id).first()
        if not allowed or not usercomm:
            return ConsumedEnergy.objects.none()

        if usercomm.administrator:
            return ConsumedEnergy.objects.filter(community__id=community_id)

        return ConsumedEnergy.objects.filter(community__id=community_id,
                                             user__id__in=[usercomm_id,
                                                           None])


class EnergyTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
        EnergyTransaction between 2 communities
        Query parameter community is expected
        /energy/transaction/?community=1
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.EnergyTransactionSerializer
    queryset = EnergyTransaction.objects.all()

    def get_queryset(self):
        community_id = self.request.query_params.get('community', None)
        allowed, response = check_user_comm_permissions(self.request, community_id)
        if not allowed:
            return EnergyTransaction.objects.none()

        return EnergyTransaction.objects.filter(
                Q(producer_community__id=community_id) |
                Q(consumer_community__id=community_id)
            )


class EnergyInvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
        EnergyInvoice
        Returns invoices for the specified usercommunity
        /energy/invoice/?usercommunity=1
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.EnergyInvoiceSerializer
    queryset = EnergyInvoice.objects.all()

    def get_queryset(self):
        usercomm_id = self.request.query_params.get('usercommunity', None)
        if not usercomm_id:
            return EnergyInvoice.objects.none()

        usercomm = UserCommunity.objects.filter(id=usercomm_id).first()
        if usercomm.administrator:
            return EnergyInvoice.objects.filter(payer__community=usercomm.community)

        return EnergyInvoice.objects.filter(payer__id=usercomm_id)


# API functions for OCPP Charge Point - Central System - Supervecina Interaction

@api_view(['GET'])
@transaction.atomic
@permission_classes((AllowAny, ))
def get_CS_pending_messages(request):
    """
        Returns pending messages for an OCPP Central System.
        Messages are related to RemoteStartTransaction, ChangeConfiguration, etc.
    """

    params = request.GET
    token = params['token']
    charge_point_id = params['cp_id']

    central_system = CentralSystem.objects.filter(token=token).first()
    charge_point = ChargePoint.objects.filter(serial_id=charge_point_id).first()
    if not central_system or not charge_point:
        return Response({'status': 'nok',
                         'error': 'Invalid Central System token or CP id'})

    pending_messages = CPMessage.objects.filter(charge_point=charge_point,
                                                central_system=central_system,
                                                sent=False)

    serialized_messages = serializers.CPMessageSerializer(pending_messages, many=True)

    for message in pending_messages:
        message.sent = True
        message.save()

    return Response({'status': 'ok', 'messages': serialized_messages.data})


@api_view(['POST'])
@permission_classes((AllowAny, ))
def save_CP_energy_consumption(request):
    """
        Receives data representing a consumption action
        redirected by the Central System from the Charge Point.
        Consumption is saved to the consumer (user community)
        and his community.
    """
    params = request.data
    token = params['token']
    date = params['datetime']
    amount = params['amount']  # meter_stop, integer in Wh
    dlt_address = params['dlt_address']
    transaction_id = params.get('transaction_id', '')
    charge_point_id = params['cp_id']

    charge_point = ChargePoint.objects.filter(serial_id=charge_point_id).first()

    user_comm = None

    if not CentralSystem.objects.filter(token=token).first():
        return Response({'status': 'nok',
                         'error': 'Invalid Central System token'})

    ev_transaction = EVTransaction.objects.filter(id=transaction_id).first()
    if not ev_transaction:
        return Response({'status': 'nok',
                         'error': 'Consumer is not identified'})

    if ev_transaction.data is not None:
        # Transaction was saved before, CP insisted with duplicated Stop
        # messages
        return Response({'status': 'ok'})

    user_comm = ev_transaction.consumer
    unit_price = user_comm.community.communityenergyinfo.in_community_energy_price

    # unit_price (W/h) multiplied by meter_stop amount
    price = float(unit_price) * float(amount)

    consume_obj = ConsumedEnergy(community=user_comm.community,
                                 energy_amount=amount,
                                 time=date,
                                 dlt_address=dlt_address,
                                 price=price,
                                 user=user_comm)
    consume_obj.save()

    ev_transaction.data = consume_obj
    ev_transaction.charge_point = charge_point
    ev_transaction.save()

    return Response({'status': 'ok'})


@api_view(['POST'])
@permission_classes((AllowAny, ))
def update_CP_status(request):
    """
        Updates status for a given Charge Point after CS received a
        StatusNotification.
    """
    params = request.data
    token = params['token']
    cp_id = params['cp_id']
    connector_id = params['connector_id']
    status = params['status'].lower()
    error_code = params['error_code']

    if not CentralSystem.objects.filter(token=token).first():
        return Response({'status': 'nok',
                         'error': 'Invalid Central System token'})

    charge_point = ChargePoint.objects.filter(serial_id=cp_id).first()
    if not charge_point:
        return Response({'status': 'nok',
                         'error': 'Charge Point is not identified'})

    if int(connector_id) == 0:  # Main controller
        charge_point.status = status
    else:
        connector, created = CPConnector.objects.get_or_create(
            charge_point=charge_point,
            connector_id=connector_id)
        connector.status = status
        connector.save()

    charge_point.error_code = error_code
    charge_point.save()

    return Response({'status': 'ok'})


@api_view(['POST'])
@permission_classes((AllowAny, ))
def authorize_CP(request):
    """
        Checks if a given CP serial id is registered.
    """
    params = request.data
    token = params['token']
    cp_id = params['cp_id']

    if not CentralSystem.objects.filter(token=token).first():
        return Response({'status': 'nok',
                         'error': 'Invalid Central System token'})

    charge_point = ChargePoint.objects.filter(serial_id=cp_id).first()
    if not charge_point:
        return Response({'status': 'nok',
                         'error': 'Charge Point is not identified'})    
    return Response({'status': 'ok'})


@api_view(['POST'])
@permission_classes((AllowAny, ))
def new_transaction(request):
    """
        Register a new EV transaction and generate a unique transaction id
        for OCPP compliance
    """
    params = request.data
    token = params['token']
    user_id = params['user_id']

    user_comm = UserCommunity.objects.filter(id=user_id).first()

    if not CentralSystem.objects.filter(token=token).first() or not user_comm:
        return Response({'status': 'nok',
                         'error': 'Invalid Central System or User ID'})

    transaction = EVTransaction(consumer=user_comm)
    transaction.save()

    return Response({'status': 'ok', 'transaction_id': transaction.id})


@api_view(['POST'])
@permission_classes((AllowAny, ))
def authorize_user(request):
    """
        Check if a given user id is registered
    """
    params = request.data
    token = params['token']
    user_id = params['user_id']
    cp_id = params['cp_id']

    user_comm = UserCommunity.objects.filter(id=user_id).first()
    charge_point = ChargePoint.objects.filter(serial_id=cp_id).first()
    central_system = CentralSystem.objects.filter(token=token).first()

    if not central_system or not user_comm or not charge_point:
        return Response({'status': 'nok',
                         'error': 'Invalid Central System or User ID'})

    if charge_point not in user_comm.community.authorized_chargepoints.all():
        return Response({'status': 'nok',
                         'error': 'User not authorized for this Charge Point'})

    return Response({'status': 'ok'})


def get_consumptions_list(user):
    """
        Retrieves the last electric consumptions for a user in all
        his communities.
    """
    response = ""
    usercomms = user.communities.all()
    for usercomm in usercomms:
        consumptions = ConsumedEnergy.objects.filter(
            user=usercomm).order_by('-time')[:10]
        # serialized = serializers.ConsumedEnergySerializer(consumptions, many=True)
        # time, energy_amount, price, community.community_address
        for consumption in consumptions:
            response += "%s - %s: %s\n" % (
                #consumption.community.community_address,
                consumption.time.strftime("%Y-%m-%d %H:%M:%S"),
                "%.2f Wh" % consumption.energy_amount,
                "€%.2f" % consumption.price)

    return response


def add_remote_start_message(user_community, charge_point_id=None):
    """
        Generates a remote start transaction message to be received by the
        CentralSystem and dispatched to the specific ChargePoint.
        user_community is the user who'll be charged for this transaction.
    """
    charge_point = None
    if not charge_point_id:
        charge_point = user_community.community.authorized_chargepoints.first()
    else:
        charge_point = ChargePoint.objects.filter(
            serial_id=charge_point_id).first()

    central_system = CentralSystem.objects.all().first()

    cp_in_comm = charge_point in user_community.community.authorized_chargepoints.all()
    if not charge_point or charge_point.status in ['unavailable', 'faulted'] or not cp_in_comm:
        return False

    CPMessage.objects.create(charge_point=charge_point,
                             central_system=central_system,
                             message="remote_start,%s" % user_community.id)
    return True
