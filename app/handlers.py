from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import status

from app.main import app
from app.shortcuts import is_htmx, redirect, render
from app.users.exceptions import LoginRequiredException


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    template = '/errors/main.html'
    status_code = exc.status_code
    context = {
        'status_code': status_code
    }

    return render(request=request, template=template, context=context)


@app.exception_handler(LoginRequiredException)
async def http_exception_handler(request, exc):
    response = redirect(f'/auth/login?next={request.url}', clear=True)
    if is_htmx(request=request):
        response.status_code = status.HTTP_200_OK
        response.headers['HX-Redirect'] = '/auth/login'
    return response
