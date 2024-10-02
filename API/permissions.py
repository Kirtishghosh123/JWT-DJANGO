from rest_framework import permissions

from API.models import CustomUser


class ConsumerPermissions(permissions.BasePermission):

    # Provide custom permission to specific endpoints

        def has_permission(self, request, view):
            user = request.user.username
            actual_user = CustomUser.objects.get(username=user)
            if actual_user.is_authenticated and actual_user is not None:
                return CustomUser.objects.filter(username=actual_user,id=actual_user.id,roles__role__iexact='consumer').exists()
            return False


class SellerPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        has_role = CustomUser.objects.filter(username=user.username, id=user.id, roles__role__iexact='seller').exists()
        print(f"User is seller: {has_role}")
        return has_role