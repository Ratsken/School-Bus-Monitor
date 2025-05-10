from rest_framework import serializers
from core.models import Bus, Route, BusLocation

class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = '__all__'  # Adjust fields based on needs

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'

class BusLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusLocation
        fields = '__all__'