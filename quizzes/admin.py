from django.contrib import admin

from .models import Category, Quiz, Question, Option


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'created_at',
    )

    search_fields = (
        'name',
    )


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'difficulty',
        'duration',
        'passing_score',
        'max_attempts',
        'status',
        'created_at',
    )

    list_filter = (
        'category',
        'difficulty',
        'status',
    )

    search_fields = (
        'title',
        'description',
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'question_text',
        'quiz',
        'marks',
        'difficulty',
        'created_at',
    )

    list_filter = (
        'quiz',
        'difficulty',
    )

    search_fields = (
        'question_text',
    )


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = (
        'option_text',
        'question',
        'is_correct',
    )

    list_filter = (
        'is_correct',
    )

    search_fields = (
        'option_text',
    )