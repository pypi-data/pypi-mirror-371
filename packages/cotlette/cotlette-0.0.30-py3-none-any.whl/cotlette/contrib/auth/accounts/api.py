from fastapi import APIRouter
from starlette.responses import JSONResponse, RedirectResponse
from cotlette.contrib.auth.users.models import UserModel
from cotlette.contrib.auth.users.utils import check_password, generate_jwt

router = APIRouter()

@router.route("/login", methods=["POST"])
async def login_user(request):
    if 'history' in request.session and len(request.session['history']):
        previous = request.session['history'].pop()
    else:
        previous = '/admin'

    form = await request.form()
    username = form["email"]
    password = form["password"]

    user = UserModel.objects.filter(email=username).first()  # type: ignore
    if not user:
        return RedirectResponse(previous, status_code=303)

    hashed_pass = user.password_hash
    valid_pass = await check_password(password, hashed_pass)
    if not valid_pass:
        return RedirectResponse(previous, status_code=303)

    if previous in ('/users/login', '/users/login/', "/"):
        previous = '/admin'

    response = RedirectResponse(previous, status_code=303)
    if valid_pass:
        response.set_cookie('jwt', generate_jwt(user.id), httponly=True)
    return response

@router.post("/logout", response_model=None)
def logout():
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie("jwt")
    return response 