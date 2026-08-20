from django import forms
from django.forms import inlineformset_factory

from quizzes.models import Category, Option, Question, Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = [
            'title',
            'description',
            'category',
            'difficulty',
            'duration',
            'passing_score',
            'max_attempts',
            'status',
        ]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            'question_text',
            'marks',
            'explanation',
            'difficulty',
        ]


OptionFormSet = inlineformset_factory(
    Question,
    Option,
    fields=['option_text', 'is_correct'],
    extra=4,
    min_num=2,
    validate_min=True,
    can_delete=True,
)
