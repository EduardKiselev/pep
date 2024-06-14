from django import template
register = template.Library()


@register.simple_tag()
def multiply(mass, nutrient_amount, *args, **kwargs):
    return round(mass * nutrient_amount / 100, 3)
