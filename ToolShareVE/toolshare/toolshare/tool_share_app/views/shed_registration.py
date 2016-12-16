import datetime

from tool_share_app import models
from tool_share_app.forms import register_shed_form
from tool_share_app.views import add_context_extra_data

from . import get_user

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


# ------------------------------
# function for the shed creation
# ------------------------------
@csrf_exempt
def register_new_shed(request):
    if not request.session['is_open']:
        return HttpResponseRedirect('/')
        
    user = get_user.get_user(request)
    
    shed_registration_form = register_shed_form.ShedRegistrar(request.POST or None)
    user_shed_tools = models.Tool.objects.all().filter(location__zip_code = user.address.zip_code)

    context = { 'shed_reg_form': shed_registration_form, 'shed_creation_page': True, }
    context.update(add_context_extra_data.add_context_extra_data(user))

    if shed_registration_form.is_valid(): 
        # form the shed address
        shed_new_address = models.Address()

        shed_new_address.street_address = shed_registration_form.cleaned_data['street_address']

        shed_new_address.state = user.address.state
        shed_new_address.city = user.address.city
        shed_new_address.zip_code = user.address.zip_code

        shed_new_address.save()

        # create the new shed
        new_shed = models.Shed()

        new_shed.name = shed_registration_form.cleaned_data['shed_name']
        new_shed.address = shed_new_address
        new_shed.coordinator = user
        
        new_shed.save()

        # make the user an admin
        user.admin = True
        
        user.save()
        
        messages.success(request, 'Shed ' + user.address.zip_code + ' "' + new_shed.name + '" successfully registered.')
        
        return HttpResponseRedirect('/user_profile')

    return render(request, 'new_shed_registration.html', context)