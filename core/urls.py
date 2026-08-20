from django.urls import path


from .views import (
    admin_analytics,
    admin_attempt_detail,
    admin_category_create,
    admin_category_delete,
    admin_category_list,
    admin_category_update,
    admin_dashboard,
    admin_question_create,
    admin_question_delete,
    admin_question_list,
    admin_question_update,
    admin_quiz_create,
    admin_quiz_delete,
    admin_quiz_list,
    admin_quiz_update,
    admin_user_list,
    admin_user_toggle_status,
    my_attempts,
    quiz_detail,
    quiz_list,
    start_quiz,
    student_dashboard,
    admin_leaderboard,
    student_performance,
)




urlpatterns = [
    path('dashboard/', admin_dashboard, name='admin_dashboard'),

    path(
        'dashboard/analytics/',
        admin_analytics,
        name='admin_analytics'
    ),

    path(
        'dashboard/quizzes/',
        admin_quiz_list,
        name='admin_quiz_list'
    ),

    path(
        'dashboard/quizzes/create/',
        admin_quiz_create,
        name='admin_quiz_create'
    ),
        path('dashboard/users/', admin_user_list, name='admin_user_list'),
    path('dashboard/users/<int:user_id>/toggle/', admin_user_toggle_status, name='admin_user_toggle_status'),

    path(
        'dashboard/quizzes/<int:quiz_id>/edit/',
        admin_quiz_update,
        name='admin_quiz_update'
    ),

    path(
        'dashboard/quizzes/<int:quiz_id>/delete/',
        admin_quiz_delete,
        name='admin_quiz_delete'
    ),
        path('dashboard/attempts/<int:attempt_id>/', admin_attempt_detail, name='admin_attempt_detail'),

    path(
        'dashboard/categories/',
        admin_category_list,
        name='admin_category_list'
    ),

    path(
        'dashboard/categories/create/',
        admin_category_create,
        name='admin_category_create'
    ),

    path(
        'dashboard/categories/<int:category_id>/edit/',
        admin_category_update,
        name='admin_category_update'
    ),

    path(
        'dashboard/categories/<int:category_id>/delete/',
        admin_category_delete,
        name='admin_category_delete'
    ),
        path('performance/', student_performance, name='student_performance'),

    path(
        'dashboard/quizzes/<int:quiz_id>/questions/',
        admin_question_list,
        name='admin_question_list'
    ),

    path(
        'dashboard/quizzes/<int:quiz_id>/questions/create/',
        admin_question_create,
        name='admin_question_create'
    ),

    path(
        'dashboard/quizzes/<int:quiz_id>/questions/<int:question_id>/edit/',
        admin_question_update,
        name='admin_question_update'
    ),

    path(
        'dashboard/quizzes/<int:quiz_id>/questions/<int:question_id>/delete/',
        admin_question_delete,
        name='admin_question_delete'
    ),

    path('quizzes/', quiz_list, name='quiz_list'),

    path('history/', my_attempts, name='my_attempts'),

    path(
        'student-dashboard/',
        student_dashboard,
        name='student_dashboard'
    ),

    path(
        'quizzes/<int:quiz_id>/',
        quiz_detail,
        name='quiz_detail'
    ),

    path(
        'quizzes/<int:quiz_id>/start/',
        start_quiz,
        name='start_quiz'
    ),
        path(
        'dashboard/leaderboard/',
        admin_leaderboard,
        name='admin_leaderboard'
    ),
]