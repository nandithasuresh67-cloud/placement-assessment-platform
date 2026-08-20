from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import admin_required, student_required
from attempts.models import Answer, Attempt
from core.forms import CategoryForm, OptionFormSet, QuestionForm, QuizForm
from quizzes.models import Category, Question, Quiz
from django.db.models import Avg, Count, Max, Q
from django.db import models
User = get_user_model()


@admin_required
def admin_dashboard(request):
    total_quizzes = Quiz.objects.count()
    total_students = User.objects.filter(role='STUDENT').count()
    total_attempts = Attempt.objects.count()

    recent_attempts = (
        Attempt.objects
        .select_related('quiz', 'user')
        .order_by('-started_at')[:10]
    )

    quizzes = Quiz.objects.select_related('category').order_by('-created_at')

    return render(
        request,
        'core/admin_dashboard.html',
        {
            'total_quizzes': total_quizzes,
            'total_students': total_students,
            'total_attempts': total_attempts,
            'recent_attempts': recent_attempts,
            'quizzes': quizzes,
        }
    )
@admin_required
def admin_user_list(request):
    students = User.objects.filter(role='STUDENT').order_by('name')

    search = request.GET.get('search')
    if search:
        students = students.filter(
            models.Q(name__icontains=search) | models.Q(email__icontains=search)
        )

    return render(
        request,
        'core/admin_user_list.html',
        {'students': students, 'search': search or ''}
    )


@admin_required
def admin_user_toggle_status(request, user_id):
    student = get_object_or_404(User, id=user_id, role='STUDENT')

    if request.method == 'POST':
        student.status = not student.status
        student.save()
        return redirect('admin_user_list')

    return render(
        request,
        'core/admin_user_confirm_toggle.html',
        {'student': student}
    )


@admin_required
def admin_quiz_list(request):
    quizzes = Quiz.objects.select_related('category').order_by('-created_at')

    return render(
        request,
        'core/admin_quiz_list.html',
        {'quizzes': quizzes}
    )


@admin_required
def admin_quiz_create(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('admin_quiz_list')
    else:
        form = QuizForm()

    return render(
        request,
        'core/admin_quiz_form.html',
        {'form': form, 'mode': 'Create'}
    )


@admin_required
def admin_quiz_update(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)

        if form.is_valid():
            form.save()
            return redirect('admin_quiz_list')
    else:
        form = QuizForm(instance=quiz)

    return render(
        request,
        'core/admin_quiz_form.html',
        {'form': form, 'mode': 'Update', 'quiz': quiz}
    )


@admin_required
def admin_quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        quiz.delete()
        return redirect('admin_quiz_list')

    return render(
        request,
        'core/admin_quiz_confirm_delete.html',
        {'quiz': quiz}
    )


@admin_required
def admin_category_list(request):
    categories = Category.objects.order_by('name')

    return render(
        request,
        'core/admin_category_list.html',
        {'categories': categories}
    )


@admin_required
def admin_category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('admin_category_list')
    else:
        form = CategoryForm()

    return render(
        request,
        'core/admin_category_form.html',
        {'form': form, 'mode': 'Create'}
    )


@admin_required
def admin_category_update(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            return redirect('admin_category_list')
    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        'core/admin_category_form.html',
        {'form': form, 'mode': 'Update', 'category': category}
    )


@admin_required
def admin_category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.delete()
        return redirect('admin_category_list')

    return render(
        request,
        'core/admin_category_confirm_delete.html',
        {'category': category}
    )


@admin_required
def admin_question_list(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.prefetch_related('options').order_by('id')

    return render(
        request,
        'core/admin_question_list.html',
        {'quiz': quiz, 'questions': questions}
    )


@admin_required
def admin_question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = OptionFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            has_correct = any(
                f.cleaned_data.get('is_correct')
                and not f.cleaned_data.get('DELETE', False)
                for f in formset.forms
                if f.cleaned_data
            )

            if not has_correct:
                form.add_error(
                    None,
                    'At least one option must be marked as correct.'
                )
            else:
                question = form.save(commit=False)
                question.quiz = quiz
                question.save()

                formset.instance = question
                formset.save()

                return redirect('admin_question_list', quiz_id=quiz.id)
    else:
        form = QuestionForm()
        formset = OptionFormSet()

    return render(
        request,
        'core/admin_question_form.html',
        {'form': form, 'formset': formset, 'mode': 'Create', 'quiz': quiz}
    )


@admin_required
def admin_question_update(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = OptionFormSet(request.POST, instance=question)

        if form.is_valid() and formset.is_valid():
            has_correct = any(
                f.cleaned_data.get('is_correct')
                and not f.cleaned_data.get('DELETE', False)
                for f in formset.forms
                if f.cleaned_data
            )

            if not has_correct:
                form.add_error(
                    None,
                    'At least one option must be marked as correct.'
                )
            else:
                form.save()
                formset.save()
                return redirect('admin_question_list', quiz_id=quiz.id)
    else:
        form = QuestionForm(instance=question)
        formset = OptionFormSet(instance=question)

    return render(
        request,
        'core/admin_question_form.html',
        {
            'form': form,
            'formset': formset,
            'mode': 'Update',
            'quiz': quiz,
            'question': question,
        }
    )


@admin_required
def admin_question_delete(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)

    if request.method == 'POST':
        question.delete()
        return redirect('admin_question_list', quiz_id=quiz.id)

    return render(
        request,
        'core/admin_question_confirm_delete.html',
        {'quiz': quiz, 'question': question}
    )


@student_required
def student_dashboard(request):
    all_attempts = Attempt.objects.filter(
        user=request.user
    ).exclude(status='IN_PROGRESS')

    total_attempts = all_attempts.count()
    passed_count = all_attempts.filter(status='PASSED').count()
    failed_count = all_attempts.filter(status='FAILED').count()

    if total_attempts > 0:
        average_percentage = round(
            sum(a.percentage for a in all_attempts) / total_attempts, 2
        )
    else:
        average_percentage = 0

    recent_attempts = (
        all_attempts
        .select_related('quiz', 'quiz__category')
        .order_by('-started_at')[:5]
    )

    attempted_quiz_ids = all_attempts.values_list(
        'quiz_id', flat=True
    ).distinct()

    recommended_quizzes = (
        Quiz.objects
        .filter(status='PUBLISHED')
        .exclude(id__in=attempted_quiz_ids)
        .select_related('category')
        .order_by('-created_at')[:4]
    )

    categories = Category.objects.all()
    category_progress = []

    for category in categories:
        category_attempts = all_attempts.filter(quiz__category=category)
        attempt_count = category_attempts.count()

        if attempt_count > 0:
            category_avg = round(
                sum(a.percentage for a in category_attempts) / attempt_count,
                2
            )
        else:
            category_avg = None

        category_progress.append({
            'name': category.name,
            'attempt_count': attempt_count,
            'average_percentage': category_avg,
        })

    return render(
        request,
        'core/student_dashboard.html',
        {
            'total_attempts': total_attempts,
            'passed_count': passed_count,
            'failed_count': failed_count,
            'average_percentage': average_percentage,
            'recent_attempts': recent_attempts,
            'recommended_quizzes': recommended_quizzes,
            'category_progress': category_progress,
        }
    )


@student_required
def my_attempts(request):
    attempts = (
        Attempt.objects
        .filter(user=request.user)
        .exclude(status='IN_PROGRESS')
        .select_related('quiz', 'quiz__category')
        .order_by('-started_at')
    )

    quiz_filter = request.GET.get('quiz')
    status_filter = request.GET.get('status')

    if quiz_filter:
        attempts = attempts.filter(quiz__id=quiz_filter)

    if status_filter:
        attempts = attempts.filter(status=status_filter)

    quizzes_attempted = (
        Quiz.objects
        .filter(attempts__user=request.user)
        .distinct()
        .order_by('title')
    )

    total_attempts = attempts.count()
    passed_count = attempts.filter(status='PASSED').count()
    failed_count = attempts.filter(status='FAILED').count()

    return render(
        request,
        'core/my_attempts.html',
        {
            'attempts': attempts,
            'quizzes_attempted': quizzes_attempted,
            'selected_quiz': quiz_filter or '',
            'selected_status': status_filter or '',
            'total_attempts': total_attempts,
            'passed_count': passed_count,
            'failed_count': failed_count,
        }
    )


@student_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(status='PUBLISHED')

    return render(
        request,
        'core/quiz_list.html',
        {'quizzes': quizzes}
    )


@student_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(
        Quiz,
        id=quiz_id,
        status='PUBLISHED'
    )

    return render(
        request,
        'core/quiz_detail.html',
        {'quiz': quiz}
    )


@student_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(
        Quiz,
        id=quiz_id,
        status='PUBLISHED'
    )

    attempt = None

    if request.method == 'GET':
        existing_attempt = Attempt.objects.filter(
            quiz=quiz,
            user=request.user,
            status='IN_PROGRESS'
        ).order_by('-started_at').first()

        if existing_attempt:
            elapsed = (
                timezone.now() - existing_attempt.started_at
            ).total_seconds()

            if elapsed <= (quiz.duration * 60) + 5:
                attempt = existing_attempt
            else:
                existing_attempt.status = 'FAILED'
                existing_attempt.completed_at = timezone.now()
                existing_attempt.time_taken = quiz.duration * 60
                existing_attempt.save()

        if attempt is None:
            completed_attempts_count = Attempt.objects.filter(
                quiz=quiz,
                user=request.user,
            ).exclude(status='IN_PROGRESS').count()

            if completed_attempts_count >= quiz.max_attempts:
                return render(
                    request,
                    'core/quiz_attempt_limit_reached.html',
                    {'quiz': quiz}
                )

    if request.method == 'POST':
        attempt_id = request.POST.get('attempt_id')

        attempt = get_object_or_404(
            Attempt,
            id=attempt_id,
            quiz=quiz,
            user=request.user,
            status='IN_PROGRESS'
        )

        questions = quiz.questions.all()

        score = 0
        correct_answers = 0
        incorrect_answers = 0
        unanswered = 0

        for question in questions:
            selected_option_id = request.POST.get(
                f'question_{question.id}'
            )

            selected_option = None

            if selected_option_id:
                selected_option = question.options.filter(
                    id=selected_option_id
                ).first()

            is_correct = (
                selected_option is not None
                and selected_option.is_correct
            )

            if selected_option is None:
                unanswered += 1
            elif is_correct:
                correct_answers += 1
                score += question.marks
            else:
                incorrect_answers += 1

            Answer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected_option,
                is_correct=is_correct
            )

        time_taken = int(
            (timezone.now() - attempt.started_at).total_seconds()
        )

        time_limit_seconds = quiz.duration * 60
        grace_seconds = 5

        if time_taken > time_limit_seconds + grace_seconds:
            time_taken = time_limit_seconds

        total_marks = sum(
            question.marks for question in questions
        )

        if total_marks > 0:
            percentage = round((score / total_marks) * 100, 2)
        else:
            percentage = 0

        if percentage >= quiz.passing_score:
            status = 'PASSED'
        else:
            status = 'FAILED'

        attempt.score = score
        attempt.percentage = percentage
        attempt.correct_answers = correct_answers
        attempt.incorrect_answers = incorrect_answers
        attempt.unanswered = unanswered
        attempt.time_taken = time_taken
        attempt.status = status
        attempt.completed_at = timezone.now()
        attempt.save()

        return render(
            request,
            'core/quiz_result.html',
            {
                'quiz': quiz,
                'attempt': attempt,
            }
        )

    if attempt is None:
        attempt = Attempt.objects.create(
            quiz=quiz,
            user=request.user
        )

    return render(
        request,
        'core/quiz_attempt.html',
        {
            'quiz': quiz,
            'attempt': attempt,
        }
    )
from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncDate


@admin_required
def admin_analytics(request):
    # ---- Top-level stats ----
    total_quizzes = Quiz.objects.count()
    total_students = User.objects.filter(role='STUDENT').count()

    completed_attempts = Attempt.objects.exclude(status='IN_PROGRESS')
    total_attempts = completed_attempts.count()
    passed_attempts = completed_attempts.filter(status='PASSED').count()

    pass_rate = (
        round((passed_attempts / total_attempts) * 100, 2)
        if total_attempts > 0 else 0
    )
    fail_rate = round(100 - pass_rate, 2) if total_attempts > 0 else 0

    average_score = (
        round(completed_attempts.aggregate(avg=Avg('percentage'))['avg'], 2)
        if total_attempts > 0 else 0
    )

    # ---- Category performance ----
    category_performance = []
    for category in Category.objects.all():
        cat_attempts = completed_attempts.filter(quiz__category=category)
        cat_count = cat_attempts.count()

        if cat_count > 0:
            cat_avg = round(
                cat_attempts.aggregate(avg=Avg('percentage'))['avg'], 2
            )
            cat_passed = cat_attempts.filter(status='PASSED').count()
            cat_pass_rate = round((cat_passed / cat_count) * 100, 2)
        else:
            cat_avg = 0
            cat_pass_rate = 0

        category_performance.append({
            'name': category.name,
            'attempt_count': cat_count,
            'average_percentage': cat_avg,
            'pass_rate': cat_pass_rate,
        })

    # ---- Quiz performance ----
    quiz_performance = []
    for quiz in Quiz.objects.select_related('category').all():
        quiz_attempts = completed_attempts.filter(quiz=quiz)
        quiz_count = quiz_attempts.count()

        if quiz_count > 0:
            quiz_avg = round(
                quiz_attempts.aggregate(avg=Avg('percentage'))['avg'], 2
            )
            quiz_passed = quiz_attempts.filter(status='PASSED').count()
            quiz_pass_rate = round((quiz_passed / quiz_count) * 100, 2)
        else:
            quiz_avg = 0
            quiz_pass_rate = 0

        quiz_performance.append({
            'title': quiz.title,
            'category': quiz.category.name if quiz.category else '—',
            'attempt_count': quiz_count,
            'average_percentage': quiz_avg,
            'pass_rate': quiz_pass_rate,
        })

    quiz_performance.sort(key=lambda q: q['attempt_count'], reverse=True)

    # ---- Student rankings (top 10 by average percentage) ----
    student_rankings = (
        User.objects
        .filter(role='STUDENT', attempts__status__in=['PASSED', 'FAILED'])
        .annotate(
            attempt_count=Count(
                'attempts',
                filter=Q(attempts__status__in=['PASSED', 'FAILED'])
            ),
            average_percentage=Avg(
                'attempts__percentage',
                filter=Q(attempts__status__in=['PASSED', 'FAILED'])
            ),
        )
        .order_by('-average_percentage')[:10]
    )

    student_rankings = [
        {
            'username': s.name,
            'attempt_count': s.attempt_count,
            'average_percentage': round(s.average_percentage, 2),
        }
        for s in student_rankings
    ]

    # ---- Attempt trends (last 30 days) ----
    trend_qs = (
        completed_attempts
        .annotate(day=TruncDate('started_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')[:30]
    )

    trend_labels = [row['day'].strftime('%b %d') for row in trend_qs]
    trend_data = [row['count'] for row in trend_qs]

    # ---- Student registrations over time (last 30 days) ----
    registration_qs = (
        User.objects
        .filter(role='STUDENT')
        .annotate(day=TruncDate('date_joined'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')[:30]
    )

    registration_labels = [row['day'].strftime('%b %d') for row in registration_qs]
    registration_data = [row['count'] for row in registration_qs]

    return render(
        request,
        'core/admin_analytics.html',
        {
            'total_quizzes': total_quizzes,
            'total_students': total_students,
            'total_attempts': total_attempts,
            'pass_rate': pass_rate,
            'fail_rate': fail_rate,
            'average_score': average_score,
            'category_performance': category_performance,
            'quiz_performance': quiz_performance,
            'student_rankings': student_rankings,
            'trend_labels': trend_labels,
            'trend_data': trend_data,
            'registration_labels': registration_labels,
            'registration_data': registration_data,
        }
    )
@admin_required
def admin_leaderboard(request):
    category_id = request.GET.get('category')

    completed_attempts = Attempt.objects.filter(status__in=['PASSED', 'FAILED'])

    if category_id:
        completed_attempts = completed_attempts.filter(quiz__category_id=category_id)

    leaderboard = (
        User.objects
        .filter(role='STUDENT', id__in=completed_attempts.values_list('user_id', flat=True))
        .annotate(
            attempt_count=Count(
                'attempts',
                filter=Q(id__in=completed_attempts.values_list('user_id', flat=True))
            ),
            average_percentage=Avg(
                'attempts__percentage',
                filter=Q(attempts__in=completed_attempts)
            ),
            highest_score=Max(
                'attempts__percentage',
                filter=Q(attempts__in=completed_attempts)
            ),
            passed_count=Count(
                'attempts',
                filter=Q(attempts__in=completed_attempts, attempts__status='PASSED')
            ),
        )
        .filter(average_percentage__isnull=False)
        .order_by('-average_percentage')
    )

    leaderboard = [
        {
            'rank': i + 1,
            'name': s.name,
            'email': s.email,
            'attempt_count': s.attempt_count,
            'average_percentage': round(s.average_percentage, 2),
            'highest_score': round(s.highest_score, 2),
            'passed_count': s.passed_count,
        }
        for i, s in enumerate(leaderboard)
    ]

    categories = Category.objects.order_by('name')

    return render(
        request,
        'core/admin_leaderboard.html',
        {
            'leaderboard': leaderboard,
            'categories': categories,
            'selected_category': int(category_id) if category_id else None,
        }
    )
@admin_required
def admin_attempt_detail(request, attempt_id):
    """Show a completed attempt, its answers, and basic answer statistics."""
    attempt = get_object_or_404(
        Attempt.objects.select_related('quiz', 'user'),
        id=attempt_id
    )

    answers = (
        Answer.objects
        .filter(attempt=attempt)
        .select_related('question', 'selected_option')
        .prefetch_related('question__options')
        .order_by('question__id')
    )

    answers = list(answers)
    answered_count = sum(
        answer.selected_option_id is not None for answer in answers
    )

    return render(
        request,
        'core/admin_attempt_detail.html',
        {
            'attempt': attempt,
            'answers': answers,
            'answer_count': len(answers),
            'answered_count': answered_count,
            'unanswered_count': len(answers) - answered_count,
        }
    )
@student_required
def student_performance(request):
    all_attempts = Attempt.objects.filter(
        user=request.user
    ).exclude(status='IN_PROGRESS')

    categories = Category.objects.all()
    category_performance = []

    for category in categories:
        cat_attempts = all_attempts.filter(quiz__category=category)
        cat_count = cat_attempts.count()

        if cat_count > 0:
            cat_avg = round(
                sum(a.percentage for a in cat_attempts) / cat_count, 2
            )
            cat_best = max(a.percentage for a in cat_attempts)
            cat_passed = cat_attempts.filter(status='PASSED').count()
        else:
            cat_avg = None
            cat_best = None
            cat_passed = 0

        category_performance.append({
            'name': category.name,
            'attempt_count': cat_count,
            'average_percentage': cat_avg,
            'best_percentage': cat_best,
            'passed_count': cat_passed,
        })

    score_trend = (
        all_attempts
        .select_related('quiz')
        .order_by('started_at')
        .values('started_at', 'percentage', 'quiz__title')
    )

    trend_labels = [a['started_at'].strftime('%b %d') for a in score_trend]
    trend_data = [float(a['percentage']) for a in score_trend]

    return render(
        request,
        'core/student_performance.html',
        {
            'category_performance': category_performance,
            'trend_labels': trend_labels,
            'trend_data': trend_data,
        }
    )