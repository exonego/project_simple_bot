import logging

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from bot.enums.roles import Role

logger = logging.getLogger(__name__)


class RoleFilter(BaseFilter):
    def __init__(self, *roles: str | Role):
        if not roles:
            raise ValueError(
                "Как минимум одна роль должна быть передана в UserRoleFilter"
            )

        self.roles = frozenset(
            Role(role) if isinstance(role, str) else role
            for role in roles
            if isinstance(role, (str, Role))
        )

        if not self.roles:
            raise ValueError("Корректные роли не были переданы в UserRoleFilter")

    async def __call__(
        self, event: Message | CallbackQuery, user_row: tuple | None
    ) -> bool:
        user = event.from_user
        if not user:
            return False

        if not user_row or not (role := user_row[2]):
            return False

        return role in self.roles
