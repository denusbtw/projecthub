import pytest

from projecthub.comments.api.v1.filters import CommentFilterSet
from projecthub.comments.models import Comment


@pytest.mark.django_db
class TestCommentFilterSet:

    def test_by_author_username(self, comment_factory, john, alice):
        john_comment = comment_factory(created_by=john)
        alice_comment = comment_factory(created_by=alice)

        queryset = Comment.objects.all()
        filtered = CommentFilterSet({"author": "jo"}, queryset=queryset).qs

        assert filtered.count() == 1
        assert filtered.first().pk == john_comment.pk