import pytest

from projecthub.conftest import todo_task_status
from projecthub.tasks.api.v1.serializers import (
    TaskListSerializer,
    TaskDetailSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskStatusCreateSerializer,
    TaskStatusListSerializer,
    TaskStatusUpdateSerializer,
)


@pytest.mark.django_db
class TestTaskListSerializer:

    def test_status_is_none(self, task_factory):
        task = task_factory(status=None)
        serializer = TaskListSerializer(task)
        assert serializer.data["status"] is None

    def test_status_is_not_none(self, task_factory, todo_task_status):
        task = task_factory(status=todo_task_status)
        serializer = TaskListSerializer(task)
        assert serializer.data["status"] == todo_task_status.name
        
    def test_create_by_is_nested_serializer(self, task_factory, user):
        task = task_factory(created_by=user)
        serializer = TaskListSerializer(task)
        assert serializer.data["created_by"]["id"] == str(user.id)


@pytest.mark.django_db
class TestTaskDetailSerializer:

    def test_status_is_none(self, task_factory):
        task = task_factory(status=None)
        serializer = TaskDetailSerializer(task)
        assert serializer.data["status"] is None

    def test_status_is_not_none(self, task_factory, todo_task_status):
        task = task_factory(status=todo_task_status)
        serializer = TaskDetailSerializer(task)
        assert serializer.data["status"] == todo_task_status.name

    def test_create_by_is_nested_serializer(self, task_factory, user):
        task = task_factory(created_by=user)
        serializer = TaskDetailSerializer(task)
        assert serializer.data["created_by"]["id"] == str(user.id)

    def test_responsible_is_nested_serializer(self, task_factory, user):
        task = task_factory(responsible=user)
        serializer = TaskDetailSerializer(task)
        assert serializer.data["responsible"]["id"] == str(user.id)


@pytest.mark.django_db
class TestTaskCreateSerializer:

    def test_to_representation_matches_list_serializer_representation(self, project):
        data = {"name": "my task"}
        serializer = TaskCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        task = serializer.save(project=project)
        assert serializer.data == TaskListSerializer(task).data


@pytest.mark.django_db
class TestTaskUpdateSerializer:

    def test_no_error_if_empty_data(self, task):
        serializer = TaskUpdateSerializer(task, data={})
        assert serializer.is_valid(), serializer.errors


@pytest.fixture
def data():
    return {"name": "test status", "code": "test_status", "order": 10}


@pytest.mark.django_db
class TestTaskStatusCreateSerializer:

    def test_to_representation_matches_list_serializer_matches(self, tenant, data):
        serializer = TaskStatusCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        task_status = serializer.save(tenant=tenant)
        assert serializer.data == TaskStatusListSerializer(task_status).data


@pytest.mark.django_db
class TestTaskStatusUpdateSerializer:

    def test_no_error_if_empty_data(self, todo_task_status, data):
        serializer = TaskStatusUpdateSerializer(todo_task_status, data={})
        assert serializer.is_valid(), serializer.errors
