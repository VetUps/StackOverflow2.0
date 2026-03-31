from django.db import transaction
from rest_framework.exceptions import PermissionDenied, NotFound

from ..models import SolutionEdits
from ..serializers import SolutionEditHistorySerializer
from .solution_service import SolutionService

class SolutionEditService:
    @staticmethod
    def get_solution_edit(solution_edit_id):
        """
        Возвращает правку по её ID
        :param solution_edit_id: ID правки
        :return:
        """
        try:
            solution_edit = SolutionEdits.objects.get(
                id=solution_edit_id
            )

            return solution_edit
        except SolutionEdits.DoesNotExist:
            raise NotFound('Такой правки не существует')

    @staticmethod
    @transaction.atomic
    def change_approve(solution_edit_id, is_approved: bool, user):
        """
        Разрешает/запрещает правку
        :param solution_edit_id: ID правки
        :param is_approved: запрет/разрешение правки
        :param user: пользователь, который совершает действие
        :return:
        """
        solution_edit = SolutionEditService.get_solution_edit(solution_edit_id)

        # Валидация
        SolutionEditService._validate_change_approve(is_approved, solution_edit, user)

        if is_approved:
            # Отклоняем все остальные правки этого решения
            SolutionEdits.objects.filter(
                solution=solution_edit.solution
            ).exclude(
                id=solution_edit.id
            ).update(
                solution_edit_is_approved=False
            )

        # Сохранение
        solution_edit.solution_edit_is_approved = is_approved
        solution_edit.save()

    @staticmethod
    def history(solution_id):
        solution = SolutionService.get_solution(solution_id)
        solution_edits = (SolutionEdits.objects
                          .filter(solution=solution, solution_edit_is_approved=True)
                          .order_by('-solution_edit_edited_at'))

        return solution_edits

    @staticmethod
    def _validate_change_approve(is_approved: bool, solution_edit, user):
        """
        Запускает все валидации для процесса смены статуса правки
        :param is_approved: is_approved: запрет/разрешение правки
        :param solution_edit: ID правки
        :param user: пользователь, который совершает действие
        :return:
        """
        SolutionEditService._can_user_approve(solution_edit, user)

    @staticmethod
    def _can_user_approve(solution_edit, user):
        """
        Проверяет права пользователя на смену статуса правки
        :param solution_edit: ID правки
        :param user: пользователь, который совершает действие
        :return:
        """
        if solution_edit.solution.user != user:
            raise PermissionDenied('Вы не можете одобрять правки для данного решения')
        return True