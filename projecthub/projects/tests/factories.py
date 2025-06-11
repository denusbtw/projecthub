from datetime import timedelta

import factory
from django.utils import timezone

from projecthub.core.models import TenantMembership
from projecthub.core.tests.factories import TenantFactory
from projecthub.projects.models import Project, ProjectMembership
from projecthub.users.tests.factories import UserFactory


def create_or_get_tenant_membership_for_user(tenant, user, created_by, updated_by):
    TenantMembership.objects.get_or_create(
        tenant=tenant,
        user=user,
        defaults={
            "role": TenantMembership.Role.USER,
            "created_by": created_by,
            "updated_by": updated_by,
        },
    )


class ProjectFactory(factory.django.DjangoModelFactory):
    owner = factory.SubFactory(UserFactory)
    supervisor = factory.SubFactory(UserFactory)
    responsible = factory.SubFactory(UserFactory)
    tenant = factory.SubFactory(TenantFactory)
    name = factory.Faker("word")
    description = factory.Faker("paragraph", nb_sentences=5)
    start_date = None
    end_date = None
    close_date = None
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Project
        skip_postgeneration_save = True

    class Params:
        now = timezone.now()

        active = factory.Trait(
            start_date=now.date() - timedelta(days=10),
            end_date=now.date() + timedelta(days=30),
            close_date=None,
            status=Project.Status.ACTIVE,
        )

        pending = factory.Trait(
            start_date=now.date() + timedelta(days=10),
            end_date=now.date() + timedelta(days=30),
            close_date=None,
            status=Project.Status.PENDING,
        )

        archived = factory.Trait(
            start_date=now.date() - timedelta(days=30),
            end_date=now.date() - timedelta(days=10),
            close_date=now - timedelta(days=5),
            status=Project.Status.ARCHIVED,
        )

    @factory.post_generation
    def create_tenant_membership(self, create, extracted, **kwargs):
        if not create:
            return

        create_or_get_tenant_membership_for_user(
            self.tenant, self.owner, self.created_by, self.updated_by
        )
        create_or_get_tenant_membership_for_user(
            self.tenant, self.supervisor, self.created_by, self.updated_by
        )


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

    @factory.post_generation
    def create_tenant_membership(self, create, extracted, **kwargs):
        if not create:
            return

        create_or_get_tenant_membership_for_user(
            self.project.tenant, self.user, self.created_by, self.updated_by
        )
