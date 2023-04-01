from functools import wraps
from starlette.exceptions import HTTPException as StarletteHttpException
from fastapi import Request, status

from app.shortcuts import is_htmx

def htmx_required(func):

    wraps(func)
    def wrapper(request: Request, *args, **kwargs):
        if not is_htmx(request=request):
            raise StarletteHttpException(status_code=status.HTTP_400_BAD_REQUEST)
        return func(request, *args, **kwargs)
    
    return wrapper
