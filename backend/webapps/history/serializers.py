from dataclasses import field
from rest_framework import serializers
from webapps.history.models import History

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['email_address','input_images','result_images','upload_time']