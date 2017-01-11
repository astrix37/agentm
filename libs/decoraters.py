from functools import wraps
from flask import g, request, redirect, url_for
import datetime
from math import pow, log
import os

def protect_view(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        key = 0
        if request.headers.get('AUTH'):
            key = request.headers['AUTH']

        if key == os.environ['KEY']:
            return fn(*args, **kwargs)

        return ('Invalid AUTH key'), 401
    return inner
