"""RBAC helpers: Anonymous / User / Premium / Staff."""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_of(user) -> str:
    if not user.is_authenticated:
        return 'anonymous'
    if user.is_staff or user.is_superuser:
        return 'staff'
    if getattr(user, 'has_premium_access', lambda: False)():
        return 'premium'
    return 'user'


def is_staff_user(user) -> bool:
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def is_premium_user(user) -> bool:
    return user.is_authenticated and (
        is_staff_user(user) or getattr(user, 'has_premium_access', lambda: False)()
    )


def staff_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not is_staff_user(request.user):
            messages.error(request, 'Staff access required.')
            return redirect('home')
        return view_func(request, *args, **kwargs)

    return _wrapped


def premium_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not is_premium_user(request.user):
            messages.warning(request, 'Premium subscription required.')
            return redirect('subscription')
        return view_func(request, *args, **kwargs)

    return _wrapped
