from rest_framework import viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny

from .models import CustomUser
from .serializers import UserRegisterSerializer

class UserViewSet(viewsets.ModelViewSet):
    @permission_classes([AllowAny])
    @action(detail=False, methods=['post'])
    def register(self, request):
        pass
