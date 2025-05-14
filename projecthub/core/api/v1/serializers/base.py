from rest_framework import serializers


class UserNestedSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField()
