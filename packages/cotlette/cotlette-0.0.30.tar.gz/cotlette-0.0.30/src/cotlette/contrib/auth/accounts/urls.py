import os

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse

# from cotlette.conf import settings
from cotlette.shortcuts import render_template
from cotlette.contrib.auth.users.forms import UserCreateForm, UserUpdateForm
from cotlette.contrib.auth.users.models import UserModel
from cotlette.contrib.auth.groups.models import GroupModel
from cotlette.contrib.auth.accounts.forms import LoginForm
from cotlette.contrib.auth.accounts.utils import hash_password, generate_jwt, check_password
from cotlette.contrib.auth.accounts.utils import get_current_user, get_current_active_user
from cotlette.contrib.auth.accounts.utils import get_current_active_superuser
from cotlette.contrib.auth.accounts.utils import get_current_user_from_token
from cotlette.contrib.auth.accounts.utils import get_current_active_user_from_token
from cotlette.contrib.auth.accounts.utils import get_current_active_superuser_from_token
from cotlette.contrib.auth.accounts.utils import get_current_user_from_cookie
from cotlette.contrib.auth.accounts.utils import get_current_active_user_from_cookie
from cotlette.contrib.auth.accounts.utils import get_current_active_superuser_from_cookie
from cotlette.contrib.auth.accounts.utils import get_current_user_from_header
from cotlette.contrib.auth.accounts.utils import get_current_active_user_from_header
from cotlette.contrib.auth.accounts.utils import get_current_active_superuser_from_header
from cotlette.contrib.auth.accounts.utils import get_current_user_from_query
from cotlette.contrib.auth.accounts.utils import get_current_active_user_from_query
from cotlette.contrib.auth.accounts.utils import get_current_active_superuser_from_query
from cotlette.contrib.auth.accounts.utils import get_current_user_from_body
from cotlette.contrib.auth.accounts.utils import get_current_active_user_from_body
from cotlette.contrib.auth.accounts.utils import get_current_active_superuser_from_body
import jwt
from jwt import PyJWTError as JWTError

from fastapi.security import OAuth2PasswordBearer


router = APIRouter()


def url_for(endpoint, **kwargs):
    """
    Функция для генерации URL на основе endpoint и дополнительных параметров.
    В данном случае endpoint игнорируется, так как мы используем только filename.
    """
    if not kwargs:
        return f"/{endpoint}"
    
    path = f"/{endpoint}"
    for key, value in kwargs.items():
        path += f"/{value}"
    
    return path


@router.get("/login", response_model=None)
async def test(request: Request):    
    return render_template(request=request, template_name="accounts/login.html", context={
        "url_for": url_for,
        "parent": "home",
        "segment": "test",
        "config": request.app.settings,
    })

@router.get("/register", response_model=None)
async def test(request: Request):    
    return render_template(request=request, template_name="accounts/register.html", context={
        "url_for": url_for,
        "parent": "home",
        "segment": "test",
        "config": request.app.settings,
    })

@router.get("/password_change", response_model=None)
async def test(request: Request):    
    return render_template(request=request, template_name="accounts/password_change.html", context={
        "url_for": url_for,
        "parent": "/",
        "segment": "test",
        "config": request.app.settings,
    })