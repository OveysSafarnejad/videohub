from typing import Optional
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from app.users.models import User
from app.shortcuts import redirect, render

from app.users.decorators import login_required
from app.users.schemas import UserLoginSchema, UserSignupSchema
from app.utils.utility import validate_schema


router = APIRouter(

)


@router.get('/users')
def users_list_view():
    return list(User.objects.all())


@router.get('/account', response_class=HTMLResponse)
@login_required
def account_view(request: Request, cookies: dict = {}):
    context = {
        "user_id": request.cookies.get("token")
    }
    return render(request=request, template='account.html', context=context)


@router.get("/auth/login", response_class=HTMLResponse)
def get_login(request: Request):

    token = request.cookies.get('token') or None
    context = {
        "is_login": token is not None
    }

    return render(request=request, template='auth/login.html', context=context)


@router.post("/auth/login", response_class=HTMLResponse)
def post_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: Optional[str]='/'
):

    raw_data = {
        "email": email,
        "password": password,
    }
    data, errors = validate_schema(raw_data, UserLoginSchema)
    context = {
        "data": data,
        "errors": errors
    }
    if len(errors):
        return render(request=request, template='auth/login.html', context=context, status_code=400)

    # TODO: find a clean way
    if 'localhost:8000' not in next:
        next = '/'

    return redirect(path=next, cookies=data)


@router.get('/auth/logout', response_class=HTMLResponse)
@login_required
def logout_get_view(request: Request):
    return render(request=request, template='/auth/logout.html', context={})


@router.post('/auth/logout', response_class=HTMLResponse)
@login_required
def logout_post_view(request: Request):
    return redirect(path='/auth/login', clear=True)


@router.get("/auth/signup", response_class=HTMLResponse)
def get_signup(request: Request):

    return render(request=request, template='auth/signup.html')


@router.post("/auth/signup", response_class=HTMLResponse)
def post_signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...)
):

    raw_data = {
        "email": email,
        "password": password,
        "password_confirm": password_confirm
    }
    data, errors = validate_schema(raw_data, UserSignupSchema)
    context = {
        'request': request,
        "data": data,
        "errors": errors
    }
    if len(errors):
        return render(request=request, template='auth/signup.html', context=context, status_code=400)
    return redirect('auth/login')
