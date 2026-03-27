from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import CustomUser
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer


class UserViewSet(viewsets.ViewSet):
    @permission_classes([AllowAny])
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes([AllowAny])
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['user_email'],
                password=serializer.validated_data['password']
            )

            if not user:
                return Response(
                    data={'errors': 'Неверные учётные данные'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not user.is_active:
                return Response(
                    data={'errors': "Аккаунт заблокирован"},
                    status=status.HTTP_403_FORBIDDEN
                )

            return Response({
                'token': 'token',
                'user': UserProfileSerializer(instance=user).data,
            },
                status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)