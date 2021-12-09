from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadIfAuthenticatedObjPerm(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return bool(request.user
                        and request.user.is_authenticated)
        return bool(request.user and request.user.is_staff)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or (request.user and request.user.is_staff)
        )


class RecipePermission(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or (request.user and request.user.is_authenticated)
        )

    def has_object_permission(self, request, view, obj):
        user = request.user

        # for TOR
        # if request.method == 'PATCH':
        #     return bool(request.user
        #                 and request.user.is_staff)

        # for frontend
        if request.method == 'PATCH':
            return bool(request.user
                        and request.user.is_authenticated)
        return bool(
            request.method in SAFE_METHODS
            or (request.user and request.user.is_staff)
            or (request.user and obj.author == user)
        )
