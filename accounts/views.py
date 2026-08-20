from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from .forms import StudentLoginForm, StudentRegistrationForm



def student_register(request):

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect('quiz_list')

    else:
        form = StudentRegistrationForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )
def student_login(request):

    if request.method == 'POST':
        form = StudentLoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user.role != 'STUDENT':
                form.add_error(
                    None,
                    'Only student accounts can use this login.'
                )
            elif not user.status:
                form.add_error(
                    None,
                    'Your account is inactive.'
                )
            else:
                login(request, user)
                return redirect('quiz_list')

    else:
        form = StudentLoginForm()

    return render(
        request,
        'accounts/login.html',
        {'form': form}
    )

def student_logout(request):
    logout(request)
    return redirect('student_login')