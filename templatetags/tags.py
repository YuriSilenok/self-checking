import subprocess

from django import template

register = template.Library()


@register.simple_tag
def version():
    return subprocess.check_output(['git', 'describe']).decode("utf-8")


@register.simple_tag
def user_type(request):
    return request.session.get('user_type', [])


@register.simple_tag
def first_name(request):
    return f" {request.session.get('first_name', 'Гость')}  {request.session.get('last_name', '')}"
