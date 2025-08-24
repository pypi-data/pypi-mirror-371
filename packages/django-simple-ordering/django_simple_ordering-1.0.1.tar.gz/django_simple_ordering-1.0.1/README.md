## Django Simple Ordering

A package for adding simple integer-based ordering to your Django models.

### Installation

Run the following command to install `django-simple-ordering` package.

`pip install django-simple-ordering`

### Usage

Follow the below steps to add ordering to your models:

1. Make sure `django_simple_ordering` and `django_object_actions` exist
   in your Django project `INSTALLED_APPS` setting. This is because this
   package relies on the [django-object-actions](https://github.com/crccheck/django-object-actions/)
   package for implementing changelist actions.

```python
INSTALLED_APPS = [
    # Django Applications ...

    "django_object_actions",
    "django_simple_ordering",

    # Your Applications ...
]
```

2. Add the `SimpleOrderingModelMixin` to your model:

```python
from django.db import models

from django_simple_ordering.models import SimpleOrderingModelMixin


class Book(SimpleOrderingModelMixin, models.Model):
    title = models.CharField(max_length=100, unique=True)

    class Meta(SimpleOrderingModelMixin.Meta):
        verbose_name = "book"
        verbose_name_plural = "books"
```

3. Add the `SimpleOrderingModelAdminMixin` to your model admin:

```python
from django.contrib import admin

from django_simple_ordering import SimpleOrderingModelAdminMixin


@admin.register(Book)
class BookAdmin(SimpleOrderingModelAdminMixin, admin.ModelAdmin):
    list_display = ("title",)
```
