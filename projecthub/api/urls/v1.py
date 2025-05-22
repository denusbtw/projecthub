from django.urls import path

from projecthub.attachments.api.views import CommentAttachmentListCreateAPIView, \
    TaskAttachmentListCreateAPIView, TaskAttachmentRetrieveDestroyAPIView, \
    CommentAttachmentRetrieveDestroyAPIView
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
    BoardListCreateAPIView,
    BoardRetrieveUpdateDestroyAPIView,
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
        "boards/", BoardListCreateAPIView.as_view(), name="board_list"
    ),
    path(
        "boards/<uuid:pk>/",
        BoardRetrieveUpdateDestroyAPIView.as_view(),
        name="board_detail"
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
    ),
    path(
        "tasks/<uuid:task_id>/attachments/",
        TaskAttachmentListCreateAPIView.as_view(),
        name="task_attachment_list"
    ),
    path(
        "tasks/<uuid:task_id>/attachments/<uuid:pk>",
        TaskAttachmentRetrieveDestroyAPIView.as_view(),
        name="task_attachment_detail"
    ),
    path(
        "comments/<uuid:comment_id>/attachments/",
        CommentAttachmentListCreateAPIView.as_view(),
        name="comment_attachment_list"
    ),
    path(
        "comments/<uuid:comment_id>/attachments/<uuid:pk>/",
        CommentAttachmentRetrieveDestroyAPIView.as_view(),
        name="comment_attachment_detail"
    )
]
