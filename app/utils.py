from functools import wraps

from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.config import get_settings

settings = get_settings()


def render(request, template_name, context=None, status_code=200, cookies=None):
    if context is None:
        context = {}
    ctx = context.copy()
    ctx.update({'request': request})
    template_dir = settings.base_dir / 'templates'
    templates = Jinja2Templates(directory=str(template_dir))
    template = templates.get_template(template_name)
    html = template.render(ctx)
    response = HTMLResponse(content=html, status_code=status_code)
    if cookies:
        for key, value in cookies.items():
            response.set_cookie(key=key, value=value, httponly=True)
    return response


def redirect(path, cookies=None, end_session=False):
    response = RedirectResponse(path, status_code=302)
    if cookies:
        for key, value in cookies.items():
            response.set_cookie(key=key, value=value, httponly=True)
    if end_session:
        response.delete_cookie('access_token')
    return response


def login_required(func):
    # preserves docstrings in wrapped function
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/auth/signin?next={request.url.path}')
        return await func(request, *args, **kwargs)
    return wrapper


def prepare_data_for_query(**kwargs):
    data = {**kwargs}
    if 'id' in data:
        data['_id'] = data.pop('id')
    return data


def get_item_or_404(collection, model, **kwargs):
    data = prepare_data_for_query(**kwargs)
    try:
        item = collection.find_one(data)
    except Exception:
        raise HTTPException(status_code=404)
    try:
        validated_item = model(**item).dict()
    except ValidationError as e:
        raise HTTPException(detail=str(e), status_code=500)
    return validated_item


def get_first_result(cursor):
    result = None
    try:
        result = cursor.next()
    except StopIteration:
        pass
    return result


def check_if_htmx(request: Request):
    return request.headers.get('hx-request') == 'true'
