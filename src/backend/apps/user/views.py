from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer


class UserViewSet(viewsets.ViewSet):
    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
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

            tokens = self.get_tokens_for_user(user)
            return Response({
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'user': UserProfileSerializer(instance=user).data,
            },
                status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        refresh = request.data.get('refresh')

        try:
            refresh = RefreshToken(refresh)
            refresh.blacklist()
            return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response({'errors': 'Токен не передан/не существует/запрещён'}, status=status.HTTP_400_BAD_REQUEST)