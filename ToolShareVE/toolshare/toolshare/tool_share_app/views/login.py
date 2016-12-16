from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from tool_share_app import models
from tool_share_app.forms import login_form
from django.shortcuts import render
from django.contrib import messages

from . import login_open_session

@csrf_exempt
def user_login(request):
    form = login_form.UserLogger(request.POST or None)

    context = {
        'login_form': form,
        'login_page': True,
    }

    if form.is_valid():
        user = models.User.objects.filter(email=form.cleaned_data['email'], password=form.cleaned_data['password'])

        if not user:
            messages.error(request, 'Invalid email or password')

        else:
            return login_open_session.login_open_session(request, form.cleaned_data['email'])

    return render(request, 'home.html', context)