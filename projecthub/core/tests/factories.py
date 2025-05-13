import factory

from projecthub.core.models import TenantMembership, Tenant
from projecthub.users.tests.factories import UserFactory


class TenantFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")
    sub_domain = factory.Sequence(lambda n: f"sub_domain_{n}")
    is_active = True
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Tenant


class TenantMembershipFactory(factory.django.DjangoModelFactory):
    tenant = factory.SubFactory(TenantFactory)
    user = factory.SubFactory(UserFactory)
    role = factory.Faker(
        "random_element", elements=[c[0] for c in TenantMembership.Role.choices]
    )
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)

    class Meta:
        model = TenantMembership
