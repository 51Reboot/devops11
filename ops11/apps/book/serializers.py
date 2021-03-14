from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ListSerializer


from .models import Publisher


class PublisherModelSerializer(ModelSerializer):

    class Meta:
        model = Publisher
        fields = "__all__"