from django.urls import path

from .views import student_login, student_logout, student_register

urlpatterns = [
    path(
        'register/',
        student_register,
        name='student_register'
    ),

    path(
        'login/',
        student_login,
        name='student_login'
    ),

    path(
        'logout/',
        student_logout,
        name='student_logout'
    ),
]