from rest_framework.permissions import BasePermission


class IsLearner(BasePermission):
    """Allow access only to users with learner role."""

    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and request.user.is_learner
        )


class IsTeacherOrAdmin(BasePermission):
    """Allow access to users with teacher or admin role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_teacher or request.user.is_admin_role)
        )
