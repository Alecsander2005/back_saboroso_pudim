from rest_framework import (
    generics,
    permissions,
    status,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(
    generics.CreateAPIView
):
    serializer_class = RegisterSerializer

    permission_classes = [
        permissions.AllowAny
    ]


class LoginView(APIView):

    permission_classes = [
        permissions.AllowAny
    ]

    def post(
        self,
        request
    ):
        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data[
            "user"
        ]

        refresh = RefreshToken.for_user(
            user
        )

        return Response(
            {
                "user": UserSerializer(
                    user
                ).data,

                "access": str(
                    refresh.access_token
                ),

                "refresh": str(
                    refresh
                ),
            },
            status=status.HTTP_200_OK
        )


class MeView(
    generics.RetrieveAPIView
):
    serializer_class = UserSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_object(self):
        return self.request.user