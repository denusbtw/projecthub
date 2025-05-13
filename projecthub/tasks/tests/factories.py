import factory

from ..models import Task, TaskStatus
from projecthub.projects.models import ProjectMembership
from projecthub.projects.tests.factories import ProjectFactory
from projecthub.users.tests.factories import UserFactory
from projecthub.core.models import TenantMembership
from projecthub.core.tests.factories import TenantFactory


class TaskStatusFactory(factory.django.DjangoModelFactory):
    tenant = factory.SubFactory(TenantFactory)
    name = factory.Faker("word")
    order = factory.Sequence(lambda n: n + 1)
    is_default = False
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)

    class Meta:
        model = TaskStatus


class TaskFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("sentence", nb_words=5)
    project = factory.SubFactory(ProjectFactory)
    status = factory.SubFactory(TaskStatusFactory)
    priority = factory.Faker("pyint", min_value=0, max_value=10)
    description = factory.Faker("paragraph", nb_sentences=3)
    responsible = factory.SubFactory(UserFactory)
    start_date = None
    end_date = None
    close_date = None
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Task
        skip_postgeneration_save = True

    @factory.post_generation
    def create_project_membership(self, created, extracted, **kwargs):
        if not created:
            return

        ProjectMembership.objects.get_or_create(
            project_id=self.project_id,
            user_id=self.responsible_id,
            defaults={
                "role": ProjectMembership.Role.USER,
                "created_by": UserFactory(),
                "updated_by": UserFactory(),
            },
        )

    @factory.post_generation
    def create_tenant_membership(self, created, extracted, **kwargs):
        if not created:
            return

        TenantMembership.objects.get_or_create(
            tenant_id=self.project.tenant_id,
            user_id=self.responsible_id,
            defaults={
                "role": TenantMembership.Role.USER,
                "created_by": UserFactory(),
                "updated_by": UserFactory(),
            },
        )
