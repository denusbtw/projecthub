from django.db.models import OuterRef, Subquery
from rest_framework import generics, permissions, exceptions

from projecthub.core.models import TenantMembership
from projecthub.projects.api.v1.serializers import (
    ProjectCreateSerializer,
    ProjectListSerializer,
    ProjectUpdateSerializer,
    ProjectDetailSerializer,
)
from projecthub.projects.api.v1.views.pagination import ProjectPagination
from projecthub.projects.models import ProjectMembership, Project


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = ProjectPagination
    #TODO: add filterset_class
    #TODO: add search by name
    #TODO: add ordering by start_date, end_date, close_date, created_at

    # TODO: move into mixin
    def initial(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise exceptions.PermissionDenied()

        self._tenant_membership = TenantMembership.objects.filter(
            tenant=self.request.tenant, user=self.request.user
        ).first()

        # 404 if request user is not admin or tenant member
        if not (request.user.is_staff or self._tenant_membership):
            raise exceptions.NotFound()

        super().initial(request, *args, **kwargs)

    # TODO: move login into permission classes
    def check_permissions(self, request):
        if request.method in permissions.SAFE_METHODS:
            return

        # admin and tenant owner can POST
        if request.user.is_staff or self._tenant_membership.is_owner:
            return

        raise exceptions.PermissionDenied()

    # TODO: move logic into Project manager
    def get_queryset(self):
        role_subquery = ProjectMembership.objects.filter(
            project_id=OuterRef("pk"), user=self.request.user
        ).values("role")[:1]

        base_queryset = Project.objects.filter(tenant=self.request.tenant).annotate(
            role=Subquery(role_subquery)
        )

        # admin and tenant owner see all projects
        if self.request.user.is_staff or self._tenant_membership.is_owner:
            return base_queryset

        # tenant members see only projects they are members of
        return base_queryset.filter(members__user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProjectCreateSerializer
        return ProjectListSerializer

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant,
            created_by=self.request.user,
            updated_by=self.request.user,
        )


class ProjectRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    #TODO: move logic into Project manager
    def get_queryset(self):
        self._tenant_membership = TenantMembership.objects.filter(
            tenant=self.request.tenant, user=self.request.user
        ).first()

        role_subquery = ProjectMembership.objects.filter(
            project_id=OuterRef("pk"), user=self.request.user
        ).values("role")[:1]

        base_queryset = Project.objects.filter(tenant=self.request.tenant).annotate(
            role=Subquery(role_subquery)
        )

        # admin and tenant owner see all projects
        if (
                self.request.user.is_staff
                or (self._tenant_membership and self._tenant_membership.is_owner)
        ):
            return base_queryset

        return base_queryset.filter(members__user=self.request.user)

    # TODO: move logic into permission classes
    def check_object_permissions(self, request, obj):
        if request.method in permissions.SAFE_METHODS:
            return

        project_membership = ProjectMembership.objects.filter(
            project=obj, user=request.user
        ).first()

        # admin, tenant owner and project owner can PUT, PATCH, DELETE
        if (
                request.user.is_staff
                or self._tenant_membership.is_owner
                or (project_membership and project_membership.is_owner)):
            return

        raise exceptions.PermissionDenied()

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return ProjectUpdateSerializer
        return ProjectDetailSerializer

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
