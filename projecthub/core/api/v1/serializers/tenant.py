from rest_framework import serializers

from projecthub.core.api.v1.serializers.base import UserNestedSerializer
from projecthub.core.models import Tenant


class BaseTenantReadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    sub_domain = serializers.CharField()
    is_active = serializers.BooleanField()


class TenantListSerializer(BaseTenantReadSerializer):
    pass


class TenantDetailSerializer(BaseTenantReadSerializer):
    owner = UserNestedSerializer()
    created_by = UserNestedSerializer()


class BaseTenantWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ("name", "sub_domain")


class TenantCreateSerializer(BaseTenantWriteSerializer):
    class Meta:
        model = Tenant
        fields = ("id", "name", "sub_domain")


class TenantUpdateSerializer(BaseTenantWriteSerializer):
    class Meta:
        model = Tenant
        fields = ("name", "sub_domain")
        extra_kwargs = {
            "name": {"required": False},
            "sub_domain": {"required": False},
        }
