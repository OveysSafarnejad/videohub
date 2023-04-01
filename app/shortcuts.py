from cassandra.cqlengine.query import (
    DoesNotExist,
    MultipleObjectsReturned
)
from fastapi import Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)
from starlette.exceptions import HTTPException as StarletteHttpException


from app import config


settings = config.get_settings()
templates = Jinja2Templates(directory=settings.templates_dir)


def is_htmx(request: Request):
    return request.headers.get('hx-request') == 'true'


def get_object_or_404(klass, **kwargs):
    try:
        _object = klass.objects.get(**kwargs)
    except DoesNotExist:
        raise StarletteHttpException(status_code=status.HTTP_404_NOT_FOUND)
    except MultipleObjectsReturned:
        raise StarletteHttpException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except:
        raise Exception('No %s matches the given query.' %
                        klass.model._meta.object_name)
    
    return _object


def redirect(path,  cookies: dict = {}, clear: bool = False):
    response = RedirectResponse(path, status_code=status.HTTP_302_FOUND)
    if len(cookies.keys()) > 0 :
        for key, value in cookies.items():
            response.set_cookie(key=key, value=value, httponly=True)
    if clear:
        response.delete_cookie('token')    

    return response

def render(request: Request, template: str, status_code: int=status.HTTP_200_OK, context: dict = {}, cookies: dict={}):

    context.update(
        {"request": request}
    )
    
    _template = templates.get_template(name=template)
    template_string = _template.render(context)
    
    response = HTMLResponse(content=template_string, status_code=status_code)
    # now we may set some cookies here
    if len(cookies.keys()) > 0:
        for k, v in cookies.items():
            response.set_cookie(key=k, value=v, httponly=True)

    return response

