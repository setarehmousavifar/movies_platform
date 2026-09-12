from rest_framework.permissions import BasePermission, SAFE_METHODS

from main.permissions import is_premium_user, is_staff_user


class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return is_staff_user(request.user)


class IsPremiumOrStaff(BasePermission):
    message = 'Premium subscription required.'

    def has_permission(self, request, view):
        return is_premium_user(request.user)


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, 'user', None)
        return owner == request.user or is_staff_user(request.user)
