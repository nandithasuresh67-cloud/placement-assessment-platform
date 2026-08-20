from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from attempts.models import Attempt
from quizzes.models import Category, Option, Question, Quiz


class AuthorizationTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            email='admin@test.com', name='Admin', password='Pass1234!'
        )
        self.student = User.objects.create_user(
            email='stud@test.com', name='Stud', password='Pass1234!', role='STUDENT'
        )

    def test_anonymous_redirected_from_admin_dashboard(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_student_forbidden_from_admin_dashboard(self):
        self.client.login(username='stud@test.com', password='Pass1234!')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_admin_dashboard(self):
        self.client.login(username='admin@test.com', password='Pass1234!')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_deactivated_student_session_is_blocked(self):
        self.client.login(username='stud@test.com', password='Pass1234!')
        self.student.status = False
        self.student.save()
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 403)


class QuizAttemptTests(TestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            email='stud@test.com', name='Stud', password='Pass1234!', role='STUDENT'
        )
        self.category = Category.objects.create(name='General')
        self.quiz = Quiz.objects.create(
            title='Sample Quiz', category=self.category, difficulty='EASY',
            duration=10, passing_score=Decimal('50.00'), max_attempts=1,
            status='PUBLISHED'
        )
        self.question = Question.objects.create(
            quiz=self.quiz, question_text='2+2?', marks=Decimal('1')
        )
        self.correct_option = Option.objects.create(
            question=self.question, option_text='4', is_correct=True
        )
        self.wrong_option = Option.objects.create(
            question=self.question, option_text='5', is_correct=False
        )
        self.client.login(username='stud@test.com', password='Pass1234!')

    def test_start_quiz_creates_attempt(self):
        response = self.client.get(reverse('start_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Attempt.objects.filter(
                quiz=self.quiz, user=self.student, status='IN_PROGRESS'
            ).exists()
        )

    def test_submission_calculates_score_correctly(self):
        self.client.get(reverse('start_quiz', args=[self.quiz.id]))
        attempt = Attempt.objects.get(quiz=self.quiz, user=self.student)

        self.client.post(reverse('start_quiz', args=[self.quiz.id]), {
            'attempt_id': attempt.id,
            f'question_{self.question.id}': self.correct_option.id,
        })

        attempt.refresh_from_db()
        self.assertEqual(attempt.status, 'PASSED')
        self.assertEqual(attempt.percentage, Decimal('100.00'))

    def test_frontend_cannot_fake_correct_answer(self):
        self.client.get(reverse('start_quiz', args=[self.quiz.id]))
        attempt = Attempt.objects.get(quiz=self.quiz, user=self.student)

        self.client.post(reverse('start_quiz', args=[self.quiz.id]), {
            'attempt_id': attempt.id,
            f'question_{self.question.id}': self.wrong_option.id,
        })

        attempt.refresh_from_db()
        self.assertEqual(attempt.status, 'FAILED')
        self.assertEqual(attempt.correct_answers, 0)

    def test_cannot_exceed_max_attempts(self):
        self.client.get(reverse('start_quiz', args=[self.quiz.id]))
        attempt = Attempt.objects.get(quiz=self.quiz, user=self.student)

        self.client.post(reverse('start_quiz', args=[self.quiz.id]), {
            'attempt_id': attempt.id,
            f'question_{self.question.id}': self.correct_option.id,
        })

        response = self.client.get(reverse('start_quiz', args=[self.quiz.id]))
        self.assertTemplateUsed(response, 'core/quiz_attempt_limit_reached.html')

    def test_unauthenticated_cannot_start_quiz(self):
        self.client.logout()
        response = self.client.get(reverse('start_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 302)