from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def _role_required(role):
    """
    Internal helper: builds a decorator that ensures the logged-in
    user has the given role. Unauthenticated users are redirected to
    login. Authenticated users with the wrong role get HTTP 403.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())

            if request.user.role != role:
                raise PermissionDenied(
                    "You do not have permission to access this page."
                )

            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
def _role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())

            if request.user.role != role or not request.user.status:
                raise PermissionDenied(
                    "You do not have permission to access this page."
                )

            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


# Usage: @admin_required above any view that only ADMIN users may access
admin_required = _role_required('ADMIN')

# Usage: @student_required above any view that only STUDENT users may access
student_required = _role_required('STUDENT')