from django import template
register = template.Library()


@register.simple_tag()
def multiply(mass, nutrient_amount, *args, **kwargs):
    if nutrient_amount:
        return round(mass * nutrient_amount / 100, 3)
    else:
        return
