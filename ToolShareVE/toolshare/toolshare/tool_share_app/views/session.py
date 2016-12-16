from tool_share_app import models
from django.http import HttpResponseRedirect


def login_open_session(request, email):
    request.session['is_open'] = True
    request.session['user_email'] = email

    return HttpResponseRedirect('/user_profile')