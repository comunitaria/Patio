# encoding: utf-8
from rest_framework import serializers
from .models import *


class GeneratedEnergySerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedEnergy
        fields = '__all__'


class ConsumedEnergySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumedEnergy
        fields = '__all__'


class EnergyTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyTransaction
        fields = '__all__'


class EnergyInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyInvoice
        fields = '__all__'


class CPMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPMessage
        fields = ('message', 'datetime')
