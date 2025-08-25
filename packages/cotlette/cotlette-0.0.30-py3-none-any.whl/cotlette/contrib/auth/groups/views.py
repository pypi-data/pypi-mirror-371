import os
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from cotlette.shortcuts import render_template
from cotlette.contrib.auth.groups.forms import GroupCreateForm, GroupUpdateForm
from cotlette.contrib.auth.groups.models import GroupModel
from cotlette.contrib.auth.users.models import UserModel
import jwt
from jwt import PyJWTError as JWTError
from datetime import timedelta, datetime
# from .utils import hash_password, generate_jwt, check_password

from starlette.responses import JSONResponse, \
    PlainTextResponse, \
    RedirectResponse, \
    StreamingResponse, \
    FileResponse, \
    HTMLResponse

from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse

router = APIRouter()

# Создание таблицы при запуске приложения
@router.on_event("startup")
async def create_tables():
    GroupModel.create_table()
    owners_group = GroupModel.objects.filter(name="Owners").first()  # type: ignore
    if not owners_group:
        GroupModel.objects.create(name="Owners")

# (Закомментированные примеры моделей и ручек оставлены для истории)
