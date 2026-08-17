from rest_framework.permissions import BasePermission


class IsAdminUserType(
    BasePermission
):
    message = (
        "Apenas administradores podem "
        "realizar esta ação."
    )

    def has_permission(
        self,
        request,
        view
    ):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.tipo_usuario == "admin"
        )