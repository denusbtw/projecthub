import factory

from projecthub.core.models import TenantMembership
from projecthub.projects.models import ProjectMembership
from projecthub.projects.tests.factories import ProjectFactory
from projecthub.users.tests.factories import UserFactory
from ..models import Task, Board


class BoardFactory(factory.django.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    name = factory.Sequence(lambda n: f"name_{n}")
    type = factory.Faker("random_element", elements=[c[0] for c in Board.Type.choices])
    order = factory.Sequence(lambda n: n + 1)
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Board


class TaskFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("sentence", nb_words=5)
    project = factory.SubFactory(ProjectFactory)
    board = factory.SubFactory(BoardFactory)
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

        if self.responsible:
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

        if self.responsible:
            TenantMembership.objects.get_or_create(
                tenant_id=self.project.tenant_id,
                user_id=self.responsible_id,
                defaults={
                    "role": TenantMembership.Role.USER,
                    "created_by": UserFactory(),
                    "updated_by": UserFactory(),
                },
            )
