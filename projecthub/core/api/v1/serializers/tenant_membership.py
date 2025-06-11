from rest_framework import serializers

from projecthub.core.api.v1.serializers.base import UserNestedSerializer
from projecthub.core.models import TenantMembership


class BaseTenantReadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    user = UserNestedSerializer()
    role = serializers.CharField(source="get_role_display")


class TenantMembershipListSerializer(BaseTenantReadSerializer):
    pass


class TenantMembershipDetailSerializer(BaseTenantReadSerializer):
    created_at = serializers.DateTimeField()


class TenantMembershipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantMembership
        fields = ("user", "role")

    def validate_user(self, user):
        tenant_owner_id = self.context["tenant_owner_id"]
        if user.pk == tenant_owner_id:
            raise serializers.ValidationError("Tenant owner cannot be a member.")
        return user


class TenantMembershipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantMembership
        fields = ("role",)
