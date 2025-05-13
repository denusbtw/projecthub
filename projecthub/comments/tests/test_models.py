import pytest
from django.db import IntegrityError


@pytest.mark.django_db
class TestComment:

    def test_error_if_comment_parent_is_self(self, comment):
        comment.parent = comment
        with pytest.raises(IntegrityError):
            comment.save()

    def test_is_reply(self, comment_factory, task):
        parent = comment_factory(task=task)
        reply = comment_factory(task=task, parent=parent)

        assert not parent.is_reply
        assert reply.is_reply
