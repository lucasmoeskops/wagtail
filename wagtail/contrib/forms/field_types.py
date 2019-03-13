import django.forms
from django.utils.formats import date_format


class AbstractFieldType:
    option_key = NotImplemented

    def create(self, field, options):
        """ Creates a new field instance for this type. """
        raise NotImplementedError()

    def email_value(self, value):
        """ Representation for value in email to user. """
        return value


class DateFieldType(AbstractFieldType):
    option_key = 'date'

    def create(self, field, options):
        return django.forms.DateField(**options)

    def email_value(self, value):
        return date_format(value, 'SHORT_DATE_FORMAT')
