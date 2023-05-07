from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.utils import render
from .client import update_index, search_index

router = APIRouter(prefix='/search')


@router.get('/', response_class=HTMLResponse)
async def home_view(request: Request, q: str | None = None):
    context = {}
    if q is not None:
        results = search_index(q)
        hits = results.get('hits') or []
        num_hits = results.get('nbHits')
        context = {
            'query': q,
            'hits': hits,
            'num_hits': num_hits
        }
    return render(request, 'search/detail.html', context)


@router.post('/update-index', response_class=HTMLResponse)
def update_index_view(request: Request):
    count = update_index(request.app.db)
    return HTMLResponse(f"({count}) Refreshed")
