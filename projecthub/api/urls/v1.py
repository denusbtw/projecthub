from django.urls import path

from projecthub.core.api.v1.views import (
    TenantListCreateAPIView, TenantRetrieveUpdateDestroyAPIView,
    TenantMembershipRetrieveUpdateDestroyAPIView
)
from projecthub.core.api.v1.views import TenantMembershipListCreateAPIView

app_name = "v1"
urlpatterns = [
    path("tenants/", TenantListCreateAPIView.as_view(), name="tenant_list"),
    path(
        "tenants/<uuid:pk>/",
        TenantRetrieveUpdateDestroyAPIView.as_view(),
        name="tenant_detail"
    ),
    path(
        "members/",
        TenantMembershipListCreateAPIView.as_view(),
        name="tenant_membership_list"
    ),
    path(
        "members/<uuid:pk>/",
        TenantMembershipRetrieveUpdateDestroyAPIView.as_view(),
        name="tenant_membership_detail"
    )
]
