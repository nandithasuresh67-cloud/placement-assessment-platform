from django.contrib import admin

from .models import Attempt, Answer


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'quiz',
        'score',
        'percentage',
        'correct_answers',
        'incorrect_answers',
        'unanswered',
        'status',
        'started_at',
        'completed_at',
    )

    list_filter = (
        'status',
        'quiz',
    )

    search_fields = (
        'user__email',
        'quiz__title',
    )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'attempt',
        'question',
        'selected_option',
        'is_correct',
    )

    list_filter = (
        'is_correct',
    )

    search_fields = (
        'question__question_text',
    )