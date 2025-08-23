from collections.abc import Callable

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from dj_raincheck.store import function_queue


def raincheck(func: Callable) -> Callable:
    """Decorator to defer function execution until after the HTTP response is sent. The decorated
    function will have a `schedule()` method that can be called to queue the function for execution.
    """

    if "dj_raincheck" not in settings.INSTALLED_APPS:
        raise ImproperlyConfigured("'dj_raincheck' must be in INSTALLED_APPS")

    def schedule(*args, **kwargs):
        if getattr(settings, "RAINCHECK_IMMEDIATE", False):
            func(*args, **kwargs)
        else:
            function_queue.append((func, args, kwargs))

    func.schedule = schedule

    return func
