from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class RegistrationLoginTests(TestCase):

    def test_student_can_register(self):
        response = self.client.post(reverse('student_register'), {
            'name': 'Test Student',
            'email': 'newstudent@test.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email='newstudent@test.com')
        self.assertEqual(user.role, 'STUDENT')
        self.assertTrue(user.status)

    def test_student_login_success(self):
        User.objects.create_user(
            email='s1@test.com', name='S1', password='Pass1234!', role='STUDENT'
        )
        response = self.client.post(reverse('student_login'), {
            'username': 's1@test.com',
            'password': 'Pass1234!',
        })
        self.assertEqual(response.status_code, 302)

    def test_admin_cannot_login_via_student_login(self):
        User.objects.create_user(
            email='admin1@test.com', name='Admin', password='Pass1234!', role='ADMIN'
        )
        response = self.client.post(reverse('student_login'), {
            'username': 'admin1@test.com',
            'password': 'Pass1234!',
        })
        self.assertContains(response, 'Only student accounts can use this login.')

    def test_inactive_student_cannot_login(self):
        User.objects.create_user(
            email='inactive@test.com', name='Inactive', password='Pass1234!',
            role='STUDENT', status=False
        )
        response = self.client.post(reverse('student_login'), {
            'username': 'inactive@test.com',
            'password': 'Pass1234!',
        })
        self.assertContains(response, 'Your account is inactive.')