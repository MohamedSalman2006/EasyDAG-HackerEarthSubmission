from rest_framework.permissions import BasePermission

class AllowGuestOrAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return True