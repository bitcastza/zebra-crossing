from rest_framework import serializers
from .models import BookedDay


class scheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookedDay
        fields = "__all__"

