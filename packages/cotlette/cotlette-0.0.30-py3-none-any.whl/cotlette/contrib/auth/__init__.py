"""
Cotlette built-in authentication (users, groups, accounts).
"""

from fastapi import APIRouter

from cotlette.contrib.auth.users import api as users_api
from cotlette.contrib.auth.groups import api as groups_api
from cotlette.contrib.auth.accounts import urls as accounts_urls
from cotlette.contrib.auth.accounts import api as accounts_api

# Импортируем модели для удобства
from cotlette.contrib.auth.users.models import UserModel, User, UserCreate
from cotlette.contrib.auth.groups.models import GroupModel, Group

__all__ = [
    'UserModel', 'User', 'UserCreate',
    'GroupModel', 'Group',
    'router'
]

router = APIRouter()

# Подключаем роуты пользователей
if hasattr(users_api, 'router'):
    router.include_router(users_api.router, prefix="/users", tags=["users"])
# Подключаем роуты групп
if hasattr(groups_api, 'router'):
    router.include_router(groups_api.router, prefix="/groups", tags=["groups"])
# Подключаем роуты аккаунтов (регистрация, аутентификация, смена пароля)
if hasattr(accounts_urls, 'router'):
    router.include_router(accounts_urls.router, prefix="/auth/accounts", tags=["accounts"])
# Подключаем роуты аккаунтов (login/logout)
if hasattr(accounts_api, 'router'):
    router.include_router(accounts_api.router, prefix="/auth/accounts", tags=["accounts"])
