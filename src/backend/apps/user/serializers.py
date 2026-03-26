from rest_framework import serializers
from .models import CustomUser

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, max_length=20, required=True)
    password_confirm = serializers.CharField(write_only=True, min_length=6, max_length=20, required=True)

    class Meta:
        model = CustomUser
        fields = ('user_name', 'user_email', 'password', 'password_confirm')

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError('Пароль не совпадают')

        if CustomUser.objects.filter(email=data['user_email']).exists():
            raise serializers.ValidationError('Пользователь с такой почтой уже существует')

    def create(self, validated_data):
        validated_data.pop('password_confirm')

        return CustomUser.objects.create(**validated_data)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('user_name', 'user_email', 'user_reputation_score', 'user_avatar_url', 'user_bio', 'user_created_at')