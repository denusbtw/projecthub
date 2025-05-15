from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, exceptions, permissions, filters

from projecthub.core.models import TenantMembership
from projecthub.projects.api.v1.filters import ProjectMembershipFilterSet
from projecthub.projects.api.v1.serializers import (
    ProjectMembershipCreateSerializer,
    ProjectMembershipListSerializer,
    ProjectMembershipUpdateSerializer,
    ProjectMembershipDetailSerializer,
)
from projecthub.projects.api.v1.views.pagination import ProjectMembershipPagination
from projecthub.projects.models import ProjectMembership


class ProjectMembershipListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = ProjectMembershipPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProjectMembershipFilterSet
    search_fields = ["user__username"]
    #TODO: add ordering by created_at

    # TODO: move into mixin
    def initial(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise exceptions.PermissionDenied()

        self._tenant_membership = TenantMembership.objects.filter(
            tenant=self.request.tenant, user=self.request.user
        ).first()

        self._project_membership = ProjectMembership.objects.filter(
            project_id=kwargs["project_id"], user=request.user
        ).first()

        # only admin, tenant owner and project member have access
        if not (
                request.user.is_staff
                or (self._tenant_membership and  self._tenant_membership.is_owner)
                or self._project_membership
        ):
            raise exceptions.NotFound()

        super().initial(request, *args, **kwargs)

    # TODO: move logic into permission classes
    def check_permissions(self, request):
        if request.method in permissions.SAFE_METHODS:
            return

        # only admin, tenant owner and project staff have access
        if (
                request.user.is_staff
                or (self._tenant_membership and self._tenant_membership.is_owner)
                or (self._project_membership and (
                        self._project_membership.is_owner
                        or self._project_membership.is_supervisor
                        or self._project_membership.is_responsible
                    )
                )
        ):
            return

        raise exceptions.PermissionDenied()

    def get_queryset(self):
        qs = ProjectMembership.objects.for_tenant(self.request.tenant)
        qs = qs.for_project(self.kwargs["project_id"])
        return qs

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProjectMembershipCreateSerializer
        return ProjectMembershipListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["project_id"] = self.kwargs["project_id"]
        return context

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.kwargs["project_id"],
            created_by=self.request.user,
            updated_by=self.request.user
        )


class ProjectMembershipRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [permissions.IsAuthenticated]

    def check_permissions(self, request):
        super().check_permissions(request)

        self._tenant_membership = TenantMembership.objects.filter(
            tenant=self.request.tenant, user=self.request.user
        ).first()

        self._project_membership = ProjectMembership.objects.filter(
            project__tenant=self.request.tenant,
            project_id=self.kwargs["project_id"],
            user=self.request.user
        ).first()

        if not (
                self.request.user.is_staff
                or (self._tenant_membership and self._tenant_membership.is_owner)
                or self._project_membership
        ):
            raise exceptions.NotFound()

    def get_queryset(self):
        qs = ProjectMembership.objects.for_tenant(self.request.tenant)
        qs = qs.for_project(self.kwargs["project_id"])
        return qs

    # TODO: move logic into permission classes
    def check_object_permissions(self, request, obj):
        if request.method in permissions.SAFE_METHODS:
            return

        if (
                request.user.is_staff
                or (self._tenant_membership and self._tenant_membership.is_owner)
                or (self._project_membership and self._project_membership.is_staff)
        ):
            return

        is_self_user = (obj.user == request.user)
        if request.method == "DELETE" and is_self_user:
            return

        raise exceptions.PermissionDenied()

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return ProjectMembershipUpdateSerializer
        return ProjectMembershipDetailSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        #TODO:
        # user can delete self
        # admin, tenant owner and project owner can delete any member
        # supervisor can delete only responsible, user, guest and reader
        # responsible can delete only user, guest and reader
        # else 403
        pass
