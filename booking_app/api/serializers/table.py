from rest_framework import serializers

from booking_app.models import Table


class TableSerializer(serializers.ModelSerializer):
    """
    Serializer for Table model.
    """

    class Meta:
        model = Table
        fields = [
            "id",
            "seats",
        ]
        read_only = True
