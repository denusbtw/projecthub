import factory
from django.utils import timezone
from faker import Faker

from projecthub.users.tests.factories import UserFactory

faker = Faker()


class AttachmentFactory(factory.django.DjangoModelFactory):
    file = factory.django.FileField(filename="test.txt", data=b"Test file content")
    uploaded_by = factory.SubFactory(UserFactory)
    uploaded_at = factory.LazyFunction(
        lambda: timezone.make_aware(faker.date_time_this_decade())
    )
    task = None
    comment = None
