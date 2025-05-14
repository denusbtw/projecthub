from rest_framework import serializers

from projecthub.core.api.v1.serializers.tenant_membership import (
    TenantMembershipListSerializer,
)
from projecthub.core.api.v1.serializers.base import UserNestedSerializer
from projecthub.core.models import Tenant, TenantMembership


class BaseTenantReadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    sub_domain = serializers.CharField()
    role = serializers.CharField()
    is_active = serializers.BooleanField()


class TenantListSerializer(BaseTenantReadSerializer):
    pass


class TenantDetailSerializer(BaseTenantReadSerializer):
    created_by = UserNestedSerializer()
    owner = serializers.SerializerMethodField()

    def get_owner(self, obj):
        owner_membership = TenantMembership.objects.filter(
            tenant=obj, role=TenantMembership.Role.OWNER
        ).first()
        if owner_membership:
            return TenantMembershipListSerializer(
                owner_membership, context=self.context
            ).data
        return None


class BaseTenantWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ("name", "sub_domain")


class TenantCreateSerializer(BaseTenantWriteSerializer):
    def to_representation(self, instance):
        request = self.context.get("request")
        instance.role = TenantMembership.Role.OWNER if request else None
        return TenantListSerializer(instance, context=self.context).data


class TenantUpdateSerializer(BaseTenantWriteSerializer):
    class Meta(BaseTenantWriteSerializer.Meta):
        extra_kwargs = {"name": {"required": False}, "sub_domain": {"required": False}}
