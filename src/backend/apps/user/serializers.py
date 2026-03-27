from rest_framework import serializers
from .models import CustomUser

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, max_length=20, required=True)
    password_confirm = serializers.CharField(write_only=True, min_length=6, max_length=20, required=True)

    class Meta:
        model = CustomUser
        fields = ('user_name', 'user_email', 'password', 'password_confirm')

    def validate_user_email(self, value):
        if CustomUser.objects.filter(user_email=value).exists():
            raise serializers.ValidationError('Пользователь с такой почтой уже существует')
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError('Пароль не совпадают')

        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')

        return CustomUser.objects.create_user(**validated_data)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('user_name', 'user_email', 'user_reputation_score', 'user_avatar_url', 'user_bio', 'user_created_at')

class UserLoginSerializer(serializers.Serializer):
    user_email = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(write_only=True, min_length=6, max_length=20, required=True)

    def validate_user_email(self, value):
        if not value.strip():
            raise serializers.ValidationError('Почта обязательна')
        return value

    def validate_password(self, value):
        if not value.strip():
            raise serializers.ValidationError('Пароль обязателен')
        return value