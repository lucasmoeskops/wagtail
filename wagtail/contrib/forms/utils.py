from importlib import import_module

from django.contrib.contenttypes.models import ContentType
from wagtail.contrib.forms.field_types import AbstractFieldType

from wagtail.core import hooks
from wagtail.core.models import UserPagePermissionsProxy, get_page_models

_FORM_CONTENT_TYPES = None


def get_form_types():
    global _FORM_CONTENT_TYPES
    if _FORM_CONTENT_TYPES is None:
        from wagtail.contrib.forms.models import AbstractForm
        form_models = [
            model for model in get_page_models()
            if issubclass(model, AbstractForm)
        ]

        _FORM_CONTENT_TYPES = list(
            ContentType.objects.get_for_models(*form_models).values()
        )
    return _FORM_CONTENT_TYPES


def get_forms_for_user(user):
    """
    Return a queryset of form pages that this user is allowed to access the submissions for
    """
    editable_forms = UserPagePermissionsProxy(user).editable_pages()
    editable_forms = editable_forms.filter(content_type__in=get_form_types())

    # Apply hooks
    for fn in hooks.get_hooks('filter_form_submissions_for_user'):
        editable_forms = fn(user, editable_forms)

    return editable_forms


def get_field_type(identifier):
    if '.' not in identifier:
        # Assume it's just a name
        return identifier

    try:
        # Try to import the field type class
        path, name = identifier.rsplit('.', maxsplit=1)
        module = import_module(path)
        klass = getattr(module, name)
        if isinstance(klass, AbstractFieldType):
            return klass
        else:
            raise ValueError('If the form field identifier uses a dot, it should be a path to a '
                             'field type.')
    except ImportError:
        raise ValueError('Invalid form field type identifier. Should be a str or a module path.')
