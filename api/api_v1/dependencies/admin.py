from fastapi import Depends

from api.api_v1.dependencies.auth import get_user_from_access_token
from api.api_v1.dependencies.users import get_user_by_username_dependency
from api.api_v1.exceptions.http_exceptions import (
    AdminOrSuperAdminRequired,
    CannotModifySelf,
    SuperAdminCanModifyOnlyAdminsOrUsers,
    AdminCanModifyOnlyUsers,
)
from core.models import User
from core.models.user import Role


async def verify_admin_dependency(
    current_user: User = Depends(get_user_from_access_token),
) -> User:
    if current_user.role not in {Role.ADMIN, Role.SUPER_ADMIN}:
        raise AdminOrSuperAdminRequired()
    return current_user


async def validate_user_modification_dependency(
    target_user: User = Depends(get_user_by_username_dependency),
    current_user: User = Depends(get_user_from_access_token),
) -> User:
    if current_user.username == target_user.username:
        raise CannotModifySelf()

    if current_user.role == Role.SUPER_ADMIN:
        if target_user.role == Role.SUPER_ADMIN:
            raise SuperAdminCanModifyOnlyAdminsOrUsers()
    elif current_user.role == Role.ADMIN:
        if target_user.role != Role.USER:
            raise AdminCanModifyOnlyUsers()
    else:
        raise AdminOrSuperAdminRequired()

    return target_user
