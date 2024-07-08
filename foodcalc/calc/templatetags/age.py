from django.template.defaultfilters import register
import datetime


@register.filter(name='age')
def age(birthday):
    """Return age in month from birthday."""
    today = (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).days
    birthday1 = (birthday - datetime.date(1970, 1, 1)).days
    return round((today-birthday1)/30.5, 1)
