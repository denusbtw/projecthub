import factory
from django.utils import timezone
from faker import Faker

from projecthub.attachments.models import TaskAttachment, CommentAttachment
from projecthub.comments.tests.factories import CommentFactory
from projecthub.tasks.tests.factories import TaskFactory
from projecthub.users.tests.factories import UserFactory

faker = Faker()


class AttachmentFactory(factory.django.DjangoModelFactory):
    file = factory.django.FileField(filename="test.txt", data=b"Test file content")
    uploaded_by = factory.SubFactory(UserFactory)
    uploaded_at = factory.LazyFunction(lambda: timezone.make_aware(
        faker.date_time_this_decade()
    ))

    class Meta:
        abstract = True


class TaskAttachmentFactory(AttachmentFactory):
    task = factory.SubFactory(TaskFactory)

    class Meta:
        model = TaskAttachment


class CommentAttachmentFactory(AttachmentFactory):
    comment = factory.SubFactory(CommentFactory)

    class Meta:
        model = CommentAttachment
