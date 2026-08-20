from django.conf import settings
from django.db import models

from quizzes.models import Quiz, Question, Option


class Attempt(models.Model):

    STATUS_CHOICES = (
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('PASSED', 'Passed'),
        ('FAILED', 'Failed'),
    )

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attempts'
    )

    score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    correct_answers = models.PositiveIntegerField(default=0)

    incorrect_answers = models.PositiveIntegerField(default=0)

    unanswered = models.PositiveIntegerField(default=0)

    time_taken = models.PositiveIntegerField(
        default=0,
        help_text='Time taken in seconds'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='IN_PROGRESS'
    )

    started_at = models.DateTimeField(auto_now_add=True)

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.email} - {self.quiz.title}"

    class Meta:
        verbose_name = 'Attempt'
        verbose_name_plural = 'Attempts'


class Answer(models.Model):

    attempt = models.ForeignKey(
        Attempt,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='attempt_answers'
    )

    selected_option = models.ForeignKey(
        Option,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='selected_answers'
    )

    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.attempt} - Question {self.question.id}"