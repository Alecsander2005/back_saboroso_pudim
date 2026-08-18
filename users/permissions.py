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

class IsOwnerAdmin(BasePermission):
    message = (
        "Apenas administradores podem "
        "realizar esta ação."
    )

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        if( 
            request.user.tipo_usuario == "admin"
        ):
            return True
        
        return obj.user == request.user