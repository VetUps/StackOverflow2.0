from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, user_email, user_name, password, **extra_fields):
        """
        Создание пользователя
        :param user_email: почта пользователя
        :param user_name: никнейм пользователя
        :param password: пароль пользователя
        :param extra_fields: дополнительные поля для создания пользователя
        :return: модель созданного пользователя
        """
        if not user_email:
            raise ValueError('Пользователь должен иметь почту')
        if not user_name:
            raise ValueError('Пользователь должен иметь никнейм')

        email = self.normalize_email(user_email)
        user = self.model(user_email=email, user_name=user_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_email, user_name, password, **extra_fields):
        """
        Создание суперпользователя с дополнительными правами
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(user_email, user_name, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель данных пользователя
    """
    class Roles(models.TextChoices):
        USER_ROLE = 'user', 'User'
        EXPERT_ROLE = 'expert', 'Expert'
        ADMIN_ROLE = 'admin', 'Admin'

    user_id =               models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, blank=False,
                                             help_text='Уникальный идентификатор пользователя')
    user_name =             models.CharField(max_length=64, unique=True, blank=False,
                                             help_text='Никнейм пользователя')
    user_email =            models.EmailField(max_length=255, unique=True, blank=False,
                                              help_text='Почта пользователя')
    user_role =             models.CharField(choices=Roles, default=Roles.USER_ROLE, max_length=15, blank=False,
                                             help_text='Роль пользователя')
    user_reputation_score = models.PositiveIntegerField(default=0, blank=False, null=False,
                                                        help_text='Репутация пользователя')
    user_avatar_url =       models.ImageField(blank=True, null=True,
                                              help_text='Аватар пользователя')
    user_bio =              models.TextField(blank=True, null=True,
                                             help_text='Дополнительная информация о пользователе')
    user_created_at =       models.DateTimeField(auto_now_add=True,
                                                 help_text='Дата регистрации пользователя')
    is_staff =              models.BooleanField(default=False)
    is_active =             models.BooleanField(default=True,
                                                help_text='Активирована ли учётная запись пользователя')

    USERNAME_FIELD='user_email'
    REQUIRED_FIELDS = ['user_name']

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.user_email

class Achievement(models.Model):
    """
    Модель данных достижений
    """
    achievement_id =          models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, blank=False,
                                               help_text='Уникальный идентификатор достижения')
    achievement_code =        models.CharField(max_length=128, blank=False, null=False, unique=True,
                                               help_text='Машиночитаемый идентификатор достижения')
    achievement_name =        models.CharField(max_length=128, blank=False, null=False,
                                               help_text='Название достижения')
    achievement_description = models.TextField(help_text='Описание достижения')

    class Meta:
        db_table = 'achievements'

    def __str__(self):
        return self.achievement_code

class UserAchievement(models.Model):
    """
    Модель данных для связки достижений и пользователей
    """
    user_achievement_id =        models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, blank=False,
                                                  help_text='Уникальный идентификатор записи')
    user =                       models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=False, null=False,
                                                   help_text='Уникальный идентификатор пользователя')
    achievement =                models.ForeignKey(Achievement, on_delete=models.CASCADE, blank=False, null=False,
                                                   help_text='Уникальный идентификатор достижения')
    user_achievement_earned_at = models.DateTimeField(auto_now_add=True,
                                                      help_text='Дата и время получения достижения')

    class Meta:
        db_table = 'user_achievements'
        constraints = [
            models.UniqueConstraint(fields=['user', 'achievement'], name='unique_user_achievement')
        ]

class ReputationTransaction(models.Model):
    class TransactionReason(models.TextChoices):
        BEST_SOLUTION = 'best_solution', 'Best solution'
        SOLUTION_UPVOTED = 'solution_upvoted', 'Solution upvoted'
        SOLUTION_DOWNVOTED = 'solution_downvoted', 'Solution downvoted'
        QUESTION_UPVOTED = 'question_upvoted', 'Question upvoted'
        ACHIEVEMENT_EARNED = 'achievement_earned', 'Achievement earned'
        ADMIN_ADJUSTMENT = 'admin_adjustment', 'Admin adjustment'


    reputation_transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, blank=False,
                                                 help_text='Уникальный идентификатор транзакции')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=False, null=False,
                             help_text='Пользователь транзакции')
    reputation_transaction_amount = models.IntegerField(blank=False, null=False,
                                                        help_text='Количество снятой/добавленной репутации')
    reputation_transaction_reason = models.CharField(max_length=128, blank=False, null=False, choices=TransactionReason.choices,
                                                     help_text='Причина начисления/снятия репутации')

    class Meta:
        db_table = 'reputation_transactions'
