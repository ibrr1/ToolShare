from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from tool_share_app import models
from tool_share_app.forms import registration_form, address_form
    
from . import login_open_session

# ---------------------------------
# function that registers new users
# ---------------------------------
@csrf_exempt
def user_registration(request):
    form_personal_info = registration_form.UserRegistrar(request.POST or None)
    form_address = address_form.AddressRegistrar(request.POST or None)

    context = {
        'registration_page': True,
        'form_address': form_address,
        'form_user_personal_information': form_personal_info,
    }

    if form_personal_info.is_valid() and form_address.is_valid():
        user = models.User() # create a new user

        # populate new user with data
        user.email = form_personal_info.cleaned_data['email']
        user.first_name = form_personal_info.cleaned_data['first_name']
        user.last_name = form_personal_info.cleaned_data['last_name']
        user.password = form_personal_info.cleaned_data['password']

        # determine if it exists
        if len(models.User.objects.filter(email=user.email)) > 0:
            messages.error(request, 'User with the email of ' + user.email + ' is already registered.')

        else:
            form_address.set_state(form_address.cleaned_data['state'])
            
            user.address = form_address.save()
            
            user.save()

            try:
                if models.Shed.objects.get(address__zip_code=user.address.zip_code):
                    return login_open_session.login_open_session(request, user.email)
                    
            except:
                pass

            # open the session
            request.session['is_open'] = True
            request.session['user_email'] = user.email
            request.session['zip_code'] = user.address.zip_code
            
            # redirect to create a new shed
            return HttpResponseRedirect('/shed_creation')

    return render(request, 'registration.html', context)

# end user_registration
