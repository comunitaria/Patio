from django.shortcuts import render
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
import requests
from . import serializers
from hashlib import md5
from comunitaria.models import UserCommunity
from comunitaria.api import check_user_comm_permissions
from .models import *



power_unit = 'W'

def get_community_from_token(token):
    community_info = CommunityEnergyInfo.objects.filter(token=token).first()

    return community_info


@api_view(['POST'])
@permission_classes((AllowAny, ))
def save_energy_action(request):
    """
        Receives data representing a generation or consumption action
        from a SCB.
    """
    params = request.data
    token = params['token']
    date = params['datetime']
    amount = params['amount']
    e_type = params['type']
    mam_address = params['mam_address']
    sensor_id = params.get('sensor_id', '')

    amount = amount.replace(power_unit, '').strip()

    community_info = get_community_from_token(token)
    if not community_info:
        return Response({'status': 'nok', 'msg': 'Invalid token'})

    if e_type == 'generated':
        gen_obj = GeneratedEnergy(community=community_info.community,
                                  energy_amount=amount,
                                  time=date,
                                  mam_address=mam_address)
        gen_obj.save()
    else:
        unit_price = community_info.in_community_energy_price
        price = (float(unit_price)/3600) * 5 * float(amount)
        user_comm = None
        if 'neighbour' in sensor_id:
            user_comm_id = sensor_id.split('_')[1]
            user_comm = community_info.community.users.filter(id=user_comm_id).first()

        consume_obj = ConsumedEnergy(community=community_info.community,
                                     energy_amount=amount,
                                     time=date,
                                     mam_address=mam_address,
                                     price=price,
                                     user=user_comm)
        consume_obj.save()
    
    return Response({'status': 'ok'})


@api_view(['POST'])
def get_pending_messages(request):
    """
        Returns pending messages for a community's SCB.
        Messages can be informative, or related to any sensor, ...
    """

    # TODO 
    
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
        allowed, response = check_user_comm_permissions(self.request, community_id)
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
        allowed, response = check_user_comm_permissions(self.request, community_id)
        if not allowed:
            return ConsumedEnergy.objects.none()

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
        return EnergyInvoice.objects.filter(payer__id=usercomm_id)
