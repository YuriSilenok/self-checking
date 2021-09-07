import subprocess

from django import template

register = template.Library()

def version():
    return subprocess.check_output(['git', 'describe']).decode("utf-8")