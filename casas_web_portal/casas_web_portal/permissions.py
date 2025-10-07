from rest_framework.permissions import (
    BasePermission,
    IsAdminUser,
    IsAuthenticated,
)

class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


def get_permissions_class(action: str):
    """Get permissions class based on action."""
    if action in ["list", "retrieve", "create"]:
        permission_classes = [IsAuthenticated]
    else:
        permission_classes = [IsSuperUser]
    return [permission() for permission in permission_classes]
