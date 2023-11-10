from . import models
from rest_framework import serializers


class TaskHubApiResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for TaskHubApiResponse
    """
    class Meta:
        model = models.TaskHubApiResponse
        fields = ['status', 'message']


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for Costumer
    """
    class Meta:
        model = models.Customer
        fields = "__all__"
