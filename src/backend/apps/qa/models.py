import uuid

from django.db import models
from ..user.models import CustomUser


class Question(models.Model):
    class Status(models.TextChoices):
        OPEN_STATUS = 'open', 'Open'
        CLOSED_STATUS = 'closed', 'Closed'
        SOLVED_STATUS = 'solved', 'Solved'

    question_id =         models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, blank=False,
                                           help_text='Уникальный идентификатор вопроса')
    user =                models.ForeignKey(CustomUser, blank=False, null=True, on_delete=models.SET_NULL,
                                            help_text='Автор вопроса')
    question_title =      models.CharField(max_length=300, blank=False,
                                           help_text='Краткое описание вопроса')
    question_body =       models.TextField(blank=False,
                                           help_text='Тело вопроса (сам текст)')
    question_status =     models.CharField(choices=Status.choices, default=Status.OPEN_STATUS, blank=False, max_length=20,
                                           help_text='Статус вопроса')
    question_created_at = models.DateTimeField(auto_now_add=True, blank=False,
                                               help_text='Дата создания вопроса')
    question_updated_at = models.DateTimeField(auto_now=True, blank=False,
                                               help_text='Дата изменения вопроса')

    class Meta:
        db_table = 'questions'

    def __str__(self):
        return self.question_title

class Solution(models.Model):
    solution_id =         models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, blank=False,
                                           help_text='Уникальный идентификатор решения')
    user =                models.ForeignKey(CustomUser, blank=False, null=True, on_delete=models.SET_NULL,
                                            help_text='Автор решения')
    question =            models.ForeignKey(Question, blank=False, on_delete=models.CASCADE,
                                            help_text='Вопрос к которому представлено решение')
    solution_body =       models.TextField(blank=False,
                                           help_text='Тело решения (сам текст)')
    solution_is_best =    models.BooleanField(default=False, blank=False,
                                              help_text='Является ли решение лучшим')
    solution_created_at = models.DateTimeField(auto_now_add=True, blank=False,
                                               help_text='Дата создания решения')
    solution_updated_at = models.DateTimeField(auto_now=True, blank=False,
                                               help_text='Дата изменения решения')

    class Meta:
        db_table = 'solutions'
        constraints = [
            models.UniqueConstraint(fields=['user', 'question'], name='unique_solution_user_pair')
        ]

    def __str__(self):
        return self.solution_id