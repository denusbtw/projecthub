from django.urls import path

from projecthub.comments.api.v1.views import CommentListCreateAPIView, \
    CommentDestroyAPIView
from projecthub.core.api.v1.views import (
    TenantListCreateAPIView, TenantRetrieveUpdateDestroyAPIView,
    TenantMembershipRetrieveUpdateDestroyAPIView, TenantMembershipListCreateAPIView
)
from projecthub.projects.api.v1.views import (
    ProjectListCreateAPIView,
    ProjectRetrieveUpdateDestroyAPIView,
    ProjectMembershipListCreateAPIView,
    ProjectMembershipRetrieveUpdateDestroyAPIView,
)
from projecthub.tasks.api.v1.views import (
    TaskListCreateAPIView,
    TaskRetrieveUpdateDestroyAPIView,
    TaskStatusListCreateAPIView,
    TaskStatusRetrieveUpdateDestroyAPIView,
)

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
    ),
    path("projects/", ProjectListCreateAPIView.as_view(), name="project_list"),
    path(
        "projects/<uuid:pk>/",
        ProjectRetrieveUpdateDestroyAPIView.as_view(),
        name="project_detail"
    ),
    path(
        "projects/<uuid:project_id>/members/",
        ProjectMembershipListCreateAPIView.as_view(),
        name="project_membership_list"
    ),
    path(
        "projects/<uuid:project_id>/members/<uuid:pk>/",
        ProjectMembershipRetrieveUpdateDestroyAPIView.as_view(),
        name="project_membership_detail"
    ),
    path(
        "projects/<uuid:project_id>/tasks/",
        TaskListCreateAPIView.as_view(),
        name="task_list"
    ),
    path(
        "projects/<uuid:project_id>/tasks/<uuid:pk>/",
        TaskRetrieveUpdateDestroyAPIView.as_view(),
        name="task_detail"
    ),
    path(
        "task-statuses/", TaskStatusListCreateAPIView.as_view(), name="task_status_list"
    ),
    path(
        "task-statuses/<uuid:pk>/",
        TaskStatusRetrieveUpdateDestroyAPIView.as_view(),
        name="task_status_detail"
    ),
    path(
        "tasks/<uuid:task_id>/comments/",
        CommentListCreateAPIView.as_view(),
        name="comment_list"
    ),
    path(
        "tasks/<uuid:task_id>/comments/<uuid:pk>/",
        CommentDestroyAPIView.as_view(),
        name="comment_detail"
    )
]
