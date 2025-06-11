import pytest
from django.core import mail

from projecthub.tasks.tasks import send_daily_task_reminders


@pytest.mark.django_db
class TestSendDailyTaskReminders:

    def test_sends_emails_correctly(self, user_factory, task_factory):
        user1 = user_factory()
        user2 = user_factory()

        task1 = task_factory(responsible=user1)
        task2 = task_factory(responsible=user1)
        task3 = task_factory(responsible=user2)

        send_daily_task_reminders()

        assert len(mail.outbox) == 2

        recipients = [email.to[0] for email in mail.outbox]
        assert {user1.email, user2.email} == set(recipients)

        content_user1 = next(
            email.body for email in mail.outbox if email.to == [user1.email]
        )
        assert task1.name in content_user1
        assert task2.name in content_user1
        assert task3.name not in content_user1
