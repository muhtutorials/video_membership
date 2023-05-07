from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .utils import render


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    status_code = exc.status_code
    template_name = 'errors/main.html'
    if status_code == 404:
        template_name = 'errors/404.html'
    context = {'status_code': status_code}
    return render(request, template_name, context, status_code=status_code)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return render(request, 'errors/404.html', status_code=404)
