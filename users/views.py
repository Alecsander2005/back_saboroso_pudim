from rest_framework import (
    generics,
    permissions,
    status,
    viewsets,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action 
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from .serializers import (
    AdminLoginSerializer,
    AdminUserSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    LogoutSerializer,
)
from .models import User
from .permissions import IsAdminUserType


class RegisterView(
    generics.CreateAPIView
):
    serializer_class = RegisterSerializer

    permission_classes = [
        permissions.AllowAny
    ]


class LoginView(APIView):

    serializer_class = LoginSerializer

    permission_classes = [
        permissions.AllowAny
    ]

    def post(
        self,
        request
    ):
        serializer = self.serializer_class(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data[
            "user"
        ]

        self.on_login(request, user)

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

    def on_login(self, request, user):
        pass


class AdminLoginView(LoginView):
    serializer_class = AdminLoginSerializer

    def on_login(self, request, user):
        auth_login(request._request, user)


class MeView(
    generics.RetrieveAPIView
):
    serializer_class = UserSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_object(self):
        return self.request.user

    @action(detail = False, methods= ["get", "path"], url_path = "me", permission_classes = [permissions.IsAuthenticated])
    def me(self,request):
        if request.method == "GET":

            serializer = UserSerializer(
                    request.user
            )

            return Response(
                serializer.data

            )

        serializer = UserSerializer(
            request.user,
            data = request.data,
            partial = True
            )

        serializer.is_valid(
            raise_exception= True
        )

        serializer.save()

        return Response(
            serializer.data
        )

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUserType]

    def perform_update(self, serializer):
        if (
            serializer.validated_data.get("is_active") is False
            and serializer.instance.pk == self.request.user.pk
        ):
            raise ValidationError({
                "is_active": "Você não pode desativar a conta que está usando."
            })

        serializer.save()


class LogoutView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def post(self,request):
        serializer = LogoutSerializer(
            data = request.data
        )

        serializer.is_valid(
            raise_exception = True
        )

        auth_logout(request._request)
        serializer.save()

        return Response({
            "detail":(
                "Logout realizado"
                "com sucesso."
            )
        },
        status=status.HTTP_200_OK
        )


        