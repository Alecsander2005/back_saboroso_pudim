from rest_framework import (
    generics,
    permissions,
    status,
    viewsets,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action 

from .serializers import (
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

        serializer.save()

        return Response({
            "detail":(
                "Logout realizado"
                "com sucesso."
            )
        },
        status=status.HTTP_200_OK
        )


        