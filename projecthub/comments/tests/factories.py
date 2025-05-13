import factory


from ..models import Comment
from projecthub.tasks.tests.factories import TaskFactory


class CommentFactory(factory.django.DjangoModelFactory):
    task = factory.SubFactory(TaskFactory)
    parent = None
    body = factory.Faker("paragraph", nb_sentences=5)
    created_by = factory.LazyAttribute(lambda o: o.task.responsible)

    class Meta:
        model = Comment
