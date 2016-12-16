import datetime
from . import forms, models
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages



def user_registration(request):
    form_personal_info = forms.UserRegistrar(request.POST or None)
    form_address = forms.AddressRegistrar(request.POST or None)

    context = {
        'form_address': form_address,
        'form_user_personal_information': form_personal_info,
        'registration_page': True
    }

    if form_personal_info.is_valid() and form_address.is_valid():
        user = models.User()

        user.email = form_personal_info.cleaned_data['email']
        user.first_name = form_personal_info.cleaned_data['first_name']
        user.last_name = form_personal_info.cleaned_data['last_name']
        user.password = form_personal_info.cleaned_data['password']

        registered = models.User.objects.filter(email=user.email)

        # check if there is an existent user with the email entered by the user trying to register
        if len(registered) > 0:
            error = 'User already registered.'
            context['error'] = error

        else:
            # link the user to the address inputted
            user.address = form_address.save()
            # store the user in the db
            user.save()

            return __login_open_session(request, user.email)

    return render(request, 'registration.html', context)


# end user_registration

def __login_open_session(request, email):
    # open the session
    request.session['is_open'] = True
    # set the universal user accessor
    request.session['user_email'] = email

    return HttpResponseRedirect('/user_profile')


# end __login_open_session


def user_login(request):
    form = forms.UserLogger(request.POST or None)

    context = {
        'login_form': form,
        'login_page': True,

    }

    if form.is_valid():
        # verify if user with the entered email and password exists
        user = models.User.objects.filter(email=form.cleaned_data['email'], password=form.cleaned_data['password'])


        if not user:
            # if not, store the error message in the context
            error = 'Invalid email or password. Please try again.'
            context['error'] = error

        else:
            return __login_open_session(request, form.cleaned_data['email'])

    return render(request, 'home.html', context)


# end user_login


def __is_session_open(request):
    # verify if a session has been open or not
    return request.session['is_open']


# end __is_session_open


def user_profile(request):
    if not __is_session_open(request):
        return HttpResponseRedirect('/')

    user = models.User.objects.get(email=request.session['user_email'])

    context = {
        'shed_coordinator': True,  # assume is a shed coordinator
        'user_profile': True
    }

    context.update(__add_general_content_to_context(user))

    sheds = models.Shed.objects.all()

    # search for a shed with the specified zip code
    for shed in sheds:
        if shed.address.zip_code == context['zip_code']:
            context['shed_name'] = shed.name
            break

    admins = models.User.objects.all().filter(admin=True)

    for admin in admins:  # go through the generated admin list
        if admin.address.zip_code == user.address.zip_code:
            context['shed_coordinator'] = False  # if the user results in not being a shed coordinator

    return render(request, 'user_profile.html', context)


# end profile


def register_new_shed(request):
    if not __is_session_open(request):
        return HttpResponseRedirect('/')

    new_shed = True  # always assument when this runs that the shed is new

    sheds = models.Shed.objects.all()  # get a list of sheds
    user = models.User.objects.get(email=request.session['user_email'])

    shed_registration_form = forms.ShedRegistrar(request.POST or None)

    context = {
        'shed_reg_form': shed_registration_form,
    }

    context.update(__add_general_content_to_context(user))

    # do not let the users create another shed, if one registered by this user
    for shed in sheds:
        if shed.coordinator.email == request.session['user_email']:
            context['error'] = 'You already created a shed named: ' + shed.name
            new_shed = False

    # if form is correct and the shed is new
    if shed_registration_form.is_valid() and new_shed:
        user_address = user.address

        shed_new_address = models.Address()

        shed_new_address.street_address = shed_registration_form.cleaned_data['street_address']
        shed_new_address.state = user_address.state
        shed_new_address.city = user_address.city
        shed_new_address.zip_code = user_address.zip_code
        shed_new_address.save()

        new_shed = models.Shed()

        new_shed.name = shed_registration_form.cleaned_data['shed_name']
        new_shed.address = shed_new_address
        new_shed.coordinator = user
        new_shed.save()

        user.admin = True  # now the user is an admin (shed's coordinator)
        user.save()
        return HttpResponseRedirect('/user_profile')

    return render(request, 'new_shed_registration.html', context)


# private function dedicated to the addition of common fields in context
def __add_general_content_to_context(user):
    context = {
        'user_first_name': user.first_name,
        'date': datetime.date.today(),
        'shed_name': 'No shed registered yet.',
        'zip_code': user.address.zip_code,
    }

    sheds = models.Shed.objects.all()

    for shed in sheds:
        if shed.address.zip_code == context['zip_code']:
            context['shed_name'] = shed.name
            break

    if user.admin == True:
        context['user_first_name'] += ' ( shed\'s coordinator )'

    return context


# end register_new_shed


def logout(request):
    request.session['is_open'] = False  # close the session
    return HttpResponseRedirect('/')


# end logout

def manage_tools_addition(request, tool_listing_type):
    if not __is_session_open(request):
        return HttpResponseRedirect('/')

    tool_form = forms.ToolAggregator(request.POST or None)

    user = models.User.objects.get(email=request.session['user_email'])

    # get the type of tool listing using tool_listing_type
    tools = __tool_listing(tool_listing_type, user)

    context = {
        'tool_form': tool_form,
        'tool_owner': user.email,
        'queryset': tools,
        'zip_code': user.address.zip_code,
        'manage_tools': True
    }

    context.update(__add_general_content_to_context(user))

    if tool_form.is_valid():
        tool_name = tool_form.cleaned_data['name']
        tool_condition = tool_form.cleaned_data['condition']
        tool_description = tool_form.cleaned_data['description']
        tool_category = tool_form.cleaned_data['category']
        is_in_shed = tool_form.cleaned_data['in_shed']

        new_tool = models.Tool()

        flag = False

        if is_in_shed == 'N':
            new_tool.location = user.address
            flag = True

        else:  # if the user wants to register the tool in the shed
            shed_list = models.Shed.objects.all()

            for shed in shed_list:
                if shed.address.zip_code == user.address.zip_code:
                    new_tool.location = shed.address
                    flag = True
                    break

        if not flag:
            context[
                'error'] = 'Tool cannot be registered. A shed must be created.'  # if a shed has not been registered in the zone
        else:
            new_tool.category = models.ToolCategory.objects.get(category=tool_category)

            # why a tool in a bad condition should be registered?
            if tool_condition == 'E':
                new_tool.condition = 'Excellent'

            elif tool_condition == 'G':
                new_tool.condition = 'Good'

            else:
                new_tool.condition = 'Regular'

            new_tool.status = 'Available'  # default status of a tool when registered
            new_tool.activate = 'Activate' # tool is Activated by default
            new_tool.name = tool_name
            new_tool.description = tool_description
            new_tool.owner = user

            new_tool.save()
            return HttpResponseRedirect('/user_profile/manage_tools/' + tool_listing_type)

    return render(request, 'manage_tools.html', context)


# end manage_tools_addition


def __tool_listing(listing_type, user):

    tools = models.Tool.objects.all()

    # all tools owned by the current user
    if listing_type == 'all_tools':
        return models.Tool.objects.all().filter(owner_id__exact=user.id)

    # all tools within the shed of a zone
    elif listing_type == 'all_tools/tools_shed':
        sheds = models.Shed.objects.all()

        for shed in sheds:
            if shed.address.zip_code == user.address.zip_code:
                return models.Tool.objects.all().filter(location=shed.address, activate='Activate')

    # all tools within a zone
    elif listing_type == 'all_tools/share_zone_tools':
        return models.Tool.objects.all().filter(
            location__in=models.Address.objects.filter(zip_code=user.address.zip_code), activate='Activate')

    else:
        return models.Tool.objects.all().filter(location=user.address)


# end __tool_listing

def manage_tools_deletion(request, tool_listing_type, tool_id):
    if not __is_session_open(request):
        return HttpResponseRedirect('/')

    tool = models.Tool.objects.all().filter(id=tool_id)
    tool.delete()

    if 'tools_shed' in tool_listing_type:
        return HttpResponseRedirect('/user_profile/manage_tools/tools_shed')

    elif 'tools_home' in tool_listing_type:
        return HttpResponseRedirect('user_profile/manage_tools/tools_home')

    else:
        return HttpResponseRedirect('/user_profile/manage_tools/all_tools')

# end manage_tools.deletion

###### User Manage Account #######

def manage_account(request):
    if not __is_session_open(request):
        return HttpResponseRedirect('/')

    user = models.User.objects.get(email=request.session['user_email'])
    shed = models.Shed.objects.filter(coordinator=user.id)
    # get the tool that have the same address as the shed
    tool = models.Tool.objects.all().filter(location=user.address)

    # put all the initial for fields in this dict
    initial_form_data = {'first_name': user.first_name,
                         'last_name': user.last_name,
                         'password': user.password,
                         'password_verification': user.password,
                         'street_address': user.address.street_address,
                         'zip_code': user.address.zip_code,
                         'state': user.address.state,
                         'city':  user.address.city,
                         }

    if request.method == 'GET':
        form_personal_info = forms.ManageAccount(initial_form_data)
        form_address = forms.AddressRegistrar(initial_form_data)

        context = {
            'form_address': form_address,
            'form_user_personal_information': form_personal_info,
            'manage_account': True
        }

        context.update(__add_general_content_to_context(user))

    if request.method == 'POST':
        form_personal_info = forms.ManageAccount(request.POST or None)
        form_address = forms.AddressRegistrar(request.POST or None)

        context = {
            'form_address': form_address,
            'form_user_personal_information': form_personal_info,
        }

        context.update(__add_general_content_to_context(user))

        if form_personal_info.is_valid() and form_address.is_valid():

            # Get the current user zup code
            user_zip_code = user.address.zip_code

            user.first_name = form_personal_info.cleaned_data['first_name']
            user.last_name = form_personal_info.cleaned_data['last_name']
            user.password = form_personal_info.cleaned_data['password']
            user.address.zip_code = form_address.cleaned_data['zip_code']

            # if the input zip code is different from the old one and if the user is an admin
            if form_address.cleaned_data['zip_code'] != user_zip_code and user.admin == True :
                # remove the admin from the user
                user.admin = False
                # delete the shed
                shed.delete()

                #link the user to the address inputted
                user.address = form_address.save()
                # store the user in the db
                user.save()

                return HttpResponseRedirect('/user_profile')

            else:
                for object in tool:
                    object.location.address = 'f'
                    object.save()




                #link the user to the address inputted
                user.address = form_address.save()
                # store the user in the db
                user.save()
                messages.success(request, 'You have successfully updated your information')
                return HttpResponseRedirect('/user_profile')

    return render(request, 'manage_account.html', context)

    # End manage account

def update_tool(request, tool_id):
    if not __is_session_open(request):
        return HttpResponseRedirect('/')

    user = models.User.objects.get(email=request.session['user_email'])
    #tool = models.Tool.objects.filter(owner=user.id)
    tool = models.Tool.objects.get(id=tool_id)

    # to know if the tool at home or at the shed
    if tool.location == user.address:
        tool_location = 'N'
    else:
        tool_location = 'Y'

    # to know get the tool condition
    if tool.condition == 'Excellent':
        tool_condition = 'E'
    elif tool.condition == 'Good':
        tool_condition = 'G'
    else:
        tool_condition = 'R'

     # to know the tool status
    if tool.status == 'Available':
        tool_status = 'Available'
    else:
        tool_status = 'Unavailable'

     # to know the tool is activate or deactivate
    if tool.activate == 'Activate':
        tool_activate = 'Activate'
    else:
        tool_activate = 'Deactivate'




    # put all the initial for fields in this dict
    initial_form_data = {'name': tool.name,
                         'description': tool.description,
                         'category': tool.category,
                         'condition': tool_condition,
                         'in_shed': tool_location,
                         'status': tool_status,
                         'activate': tool_activate
                         }

    if request.method == 'GET':
        tool_form = forms.UpdateTool(initial_form_data)
        tool_form2 = forms.UpdateTool2(initial_form_data)

        context = {
            'tool_form': tool_form,
            'tool_form2': tool_form2,
            'manage_tools': True
        }

        context.update(__add_general_content_to_context(user))

    if request.method == 'POST':
        tool_form = forms.UpdateTool(request.POST or None)
        tool_form2 = forms.UpdateTool2(request.POST or None)

        context = {
            'tool_form': tool_form,
            'tool_form2': tool_form2,
        }

        context.update(__add_general_content_to_context(user))

        if tool_form.is_valid() and tool_form2.is_valid():
            tool_name = tool_form.cleaned_data['name']
            tool_condition = tool_form2.cleaned_data['condition']
            tool_description = tool_form.cleaned_data['description']
            tool_category = tool_form.cleaned_data['category']
            is_in_shed = tool_form2.cleaned_data['in_shed']
            tool_status = tool_form2.cleaned_data['status']
            tool_activate = tool_form2.cleaned_data['activate']

            flag = False

            if is_in_shed == 'N':
                tool.location = user.address
                flag = True

            else:  # if the user wants to register the tool in the shed
                shed_list = models.Shed.objects.all()

                for shed in shed_list:
                    if shed.address.zip_code == user.address.zip_code:
                        tool.location = shed.address
                        flag = True
                        break

            if not flag:
                context[
                    'error'] = 'Tool cannot be registered. A shed must be created.'  # if a shed has not been registered in the zone
            else:
                tool.category = models.ToolCategory.objects.get(category=tool_category)

                # why a tool in a bad condition should be registered?
                if tool_condition == 'E':
                    tool.condition = 'Excellent'

                elif tool_condition == 'G':
                    tool.condition = 'Good'

                else:
                    tool.condition = 'Regular'

                tool.status = tool_status  # update the tool  status
                tool.activate = tool_activate # update the tool activate
                tool.name = tool_name
                tool.description = tool_description
                tool.owner = user
                tool.save()

            messages.success(request, 'You have successfully updated your tool')

            return HttpResponseRedirect('/user_profile/manage_tools/all_tools/')

    return render(request, 'update_tool.html', context)

    # End update tool

