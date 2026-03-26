from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password, **extra_fields):
        """
        Создание пользователя
        :param email: почта пользователя
        :param username: никнейм пользователя
        :param password: пароль пользователя
        :param extra_fields: дополнительные поля для создания пользователя
        :return: модель созданного пользователя
        """
        if not email:
            raise ValueError('The user must have an email address')
        if not username:
            raise ValueError('The user must have an username')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        """
        Создание суперпользователя с дополнительными правами
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser):
    """
    Кастомная модель пользователя
    """

    USER_ROLE = 'user'
    EXPERT_ROLE = 'expert'
    ADMIN_ROLE = 'admin'

    ROLE_CHOICES = {
        USER_ROLE: 'User',
        EXPERT_ROLE: 'Expert',
        ADMIN_ROLE: 'Admin',
    }

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, blank=False,
                               help_text='Уникальный идентификатор пользователя')
    user_username = models.CharField(max_length=64, unique=True, blank=False,
                                     help_text='Никнейм пользователя')
    user_email = models.EmailField(max_length=255, unique=True, blank=False,
                                   help_text='Почта пользователя')
    user_role = models.CharField(choices=ROLE_CHOICES, default=USER_ROLE, max_length=15, blank=False,
                                 help_text='Роль пользователя')
    user_reputation_score = models.IntegerField(default=0, blank=False, null=False)
    user_avatar_url = models.ImageField(blank=True, help_text='Аватар пользователя')
    user_bio = models.TextField(blank=True, help_text='Дополнительная информация о пользователе')
    user_is_blocked = models.BooleanField(default=False, blank=False, null=False)
    user_created_at = models.DateTimeField(auto_now_add=True)
