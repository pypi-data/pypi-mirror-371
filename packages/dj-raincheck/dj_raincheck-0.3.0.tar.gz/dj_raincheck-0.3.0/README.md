# dj-raincheck

> Simple asynchronous execution in Django

Background tasks are great, but often they are overpowered for the task at hand, and require more complicated setup.

`dj-raincheck` is a simpler alternative. It will execute code after the request is complete, without the need for additional background tasks, daemons, or queues.

NOTE: `dj-raincheck` is a fork of [django-after-response](https://github.com/defrex/django-after-response) which fixes a few bugs, provides a more modern Python package, and support for newer Django versions.

## Installation

```shell
uv add dj-raincheck

OR

pip install dj-raincheck
```

## Usage

1. Add `dj_raincheck` to your `INSTALLED_APPS` in `settings.py`.

```python
# settings.py

INSTALLED_APPS = (
    ...
    "dj_raincheck",
)
```

2. Create a function that you want to run after the current request/response lifecycle.

```python
# tasks.py

from django.core.mail import send_mail
from dj_raincheck import raincheck

@raincheck
def send_email(to: str, subject: str, body: str) -> None:
    send_mail(subject, body, 'me@example.com', [to])
```

3. Queue the function in view code to be run after the current request/response lifecycle by calling its `schedule` method and passing in the necessary args or kwargs.

```python
# views.py

from .tasks import send_email

# Function-based view example
def index(request):
    ...

    send_email.schedule('customer@example.com', 'Confirm Signup', body)

    return render(...)

# Class-based view example
class IndexView(View):
    def get(self, request, *args, **kwargs):
        ...
        
        send_email.schedule('customer@example.com', 'Confirm Signup', body)

        return render(...)
```

## Settings

### `RAINCHECK_RUN_ASYNC`

`True` by default. Set to `False` to execute the jobs in the current thread as opposed to starting a new thread for each function.

NOTE: This is primarily for debugging purposes. When set to `False`, Django will wait for all scheduled functions to complete before closing the request, which can significantly increase response times.

### `RAINCHECK_IMMEDIATE`

`False` by default. Set to `True` to execute scheduled functions immediately when `schedule()` is called, rather than queuing them to run after the response is completed.

NOTE: When set to `True`, functions will execute synchronously during the request/response cycle.
