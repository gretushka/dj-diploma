from django import template

register = template.Library()


@register.filter(name='times')
def times(number):
    number = int(number)
    return range(number)


@register.filter(name='range1to10')
def range1to10(number):
    return range(2, min(10, number))
