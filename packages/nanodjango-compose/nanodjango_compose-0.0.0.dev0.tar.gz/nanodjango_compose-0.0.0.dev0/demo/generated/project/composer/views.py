import inspect
from functools import wraps

from django.http import HttpResponse


def ensure_http_response(view_fn):
    """
    If a view returns a plain string value, convert it into an HttpResponse
    """
    if inspect.iscoroutinefunction(view_fn):

        @wraps(view_fn)
        async def wrapped(*args, **kwargs):
            response = await view_fn(*args, **kwargs)
            if isinstance(response, HttpResponse):
                return response
            return HttpResponse(response)

    else:

        @wraps(view_fn)
        def wrapped(*args, **kwargs):
            response = view_fn(*args, **kwargs)
            if isinstance(response, HttpResponse):
                return response
            return HttpResponse(response)

    return wrapped


@ensure_http_response
def hello_world(request):
    return "<p>Hello, World!</p>"
