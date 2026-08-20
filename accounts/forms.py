from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import User


class StudentRegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            'name',
            'email',
            'password1',
            'password2',
        )
class StudentLoginForm(AuthenticationForm):

    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Enter your email'
            }
        )
    )
    def save(self, commit=True):
        user = super().save(commit=False)

        user.role = 'STUDENT'
        user.status = True

        if commit:
            user.save()

        return user