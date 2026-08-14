from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer


class CurrentUserView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request):
        serializer = UserSerializer(request.user)

        return Response(serializer.data)