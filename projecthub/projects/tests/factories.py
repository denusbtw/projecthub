import factory

from projecthub.core.models import TenantMembership
from projecthub.core.tests.factories import TenantFactory
from projecthub.projects.models import Project, ProjectMembership
from projecthub.users.tests.factories import UserFactory


class ProjectFactory(factory.django.DjangoModelFactory):
    tenant = factory.SubFactory(TenantFactory)
    name = factory.Faker("word")
    status = factory.Faker(
        "random_element", elements=[c[0] for c in Project.Status.choices]
    )
    description = factory.Faker("paragraph", nb_sentences=5)
    start_date = None
    end_date = None
    close_date = None
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Project


class ProjectMembershipFactory(factory.django.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    user = factory.SubFactory(UserFactory)
    role = factory.Faker(
        "random_element", elements=[c[0] for c in ProjectMembership.Role.choices]
    )
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)

    class Meta:
        model = ProjectMembership
        skip_postgeneration_save = True

    # TODO: test
    @factory.post_generation
    def create_tenant_membership(self, create, extracted, **kwargs):
        if not create:
            return

        TenantMembership.objects.get_or_create(
            tenant_id=self.project.tenant_id,
            user=self.user,
            defaults={
                "role": TenantMembership.Role.USER,
                "created_by": self.created_by,
                "updated_by": self.updated_by,
            },
        )
