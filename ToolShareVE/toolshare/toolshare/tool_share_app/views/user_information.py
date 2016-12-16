from tool_share_app import models

from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import get_user, add_context_extra_data


# ---------------------------------------------------------
# function dedicated to the acquisicion of user information
# ---------------------------------------------------------
def user_information(request, user_id):
    if not request.session['is_open']:
        return HttpResponseRedirect('/')
        
    context = {} # empty context

    return render(request, 
                  'user_information.html', 
                  context.update(add_context_extra_data.add_context_extra_data(get_user.get_user(request))))