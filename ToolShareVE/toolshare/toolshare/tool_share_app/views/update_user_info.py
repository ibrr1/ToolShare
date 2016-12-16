from tool_share_app import models
from tool_share_app.forms import update_user_info_form, address_form
from django.shortcuts import render
from django.http import HttpResponseRedirect
from tool_share_app.views import add_context_extra_data
from django.contrib import messages

from . import tool_requested, notification_num, get_user
from django.views.decorators.csrf import csrf_exempt



# -----------------------------------
# function that updates the user info
# -----------------------------------
@csrf_exempt
def manage_account(request):
    if not request.session['is_open']:
        return HttpResponseRedirect('/')
        
    form_address = None
    form_personal_info = None
    
    user = get_user.get_user(request)
    
    shed = models.Shed.objects.get(address__zip_code=user.address.zip_code)
    
    user_home_tools = models.Tool.objects.all().filter(location=user.address)
    
    user_zip_code = user.address.zip_code

    initial_form_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'street_address': user.address.street_address,
            'zip_code': user.address.zip_code,
            'state': user.address.state.id,
            'city': user.address.city,
    }
    
    context = {
            'tool_requested_number': tool_requested.tool_requested(user),
            'form_user_personal_information': form_personal_info
    }
    
    context.update(add_context_extra_data.add_context_extra_data(user))
    
    if request.method == 'GET':
        form_address = address_form.AddressRegistrar(initial_form_data)
        form_personal_info = update_user_info_form.ManageAccount(initial_form_data)

        context['manage_account'] = True
        context['form_address'] = form_address
        context['form_user_personal_information'] = form_personal_info
        context['num_notification'] = notification_num.notification_num(user)
        
    if request.method == 'POST':
        form_address = address_form.AddressRegistrar(request.POST or None)
        form_personal_info = update_user_info_form.ManageAccount(request.POST or None)
        
        context['h'] = True
        context['form_address'] = form_address
        context['form_user_personal_information'] = form_personal_info
        context['num_notification'] = notification_num.notification_num(user)

        if form_personal_info.is_valid() and form_address.is_valid():
            existent_shed = None
            user.first_name = form_personal_info.cleaned_data['first_name']
            user.last_name = form_personal_info.cleaned_data['last_name']
            
            preivous_zip_code = user.address.zip_code
            
            user.address.zip_code = form_address.cleaned_data['zip_code']

            if preivous_zip_code != user.address.zip_code:
                if not verify_tool_status(user):
                    messages.error(request, 'All your tools should be returned before leaving the current share zone.')
                    
                    return HttpResponseRedirect('/user_profile/update_account/')
                    
                elif not verify_borrowed_tools(user):
                    messages.error(request, 'You have to return all your borrowed tools before leaving the current share zone.')
                    
                    return HttpResponseRedirect('/user_profile/update_account/')
                    
            verify_tool_requests(user)

            if user.address.zip_code != user_zip_code and user.admin == True:
                num_admin = 0
                
                all_possible_admins = models.User.objects.all().filter(admin=True)

                for possible_admin in all_possible_admins:
                    if possible_admin.admin == True and possible_admin.address.zip_code == models.User.objects.get(email=request.session['user_email']).address.zip_code:
                        num_admin = num_admin + 1

                if (num_admin - 1) >= 1:
                    user.admin = False
                    
                    try:
                        existent_shed = models.Shed.objects.get(address__zip_code=user_zip_code)
                        
                    except:
                        pass
                        
                    form_address.set_state(form_address.cleaned_data['state'])
                    
                    prev_user_address = user.address

                    user.address = form_address.save()

                    user.save()

                    for tool in user_home_tools:
                        tool.location = user.address
                        tool.save()
                    
                    if existent_shed:
                        user_shed_to_user = None
                        user_shed_tools = models.Tool.objects.all().filter(location=shed.address)
                        
                        try:
                            new_shed_to_user = models.Shed.objects.get(address__zip_code=user.address.zip_code)
                        
                            for tool in user_shed_tools:
                                if tool.location == existent_shed.address:
                                    tool.location = new_shed_to_user.address
                                    
                                    tool.save() 
                            
                            messages.success(request, 'You have successfully updated your information')
                            
                        except:
                            pass
                                
                    prev_user_address.delete()

                    delete_me_from_statistics(user)

                    return HttpResponseRedirect('/user_profile')
                    
                else:
                
                    messages.error(request, 'Please add another shed admin before leaving the shed')
                
                    return render(request, 'manage_account.html', context)

            elif form_address.cleaned_data['zip_code'] != user_zip_code:
                try:
                    existent_shed = models.Shed.objects.get(address__zip_code=user_zip_code)
                    
                except:
                    pass

                prev_user_address = user.address

                form_address.set_state(form_address.cleaned_data['state'])

                user.address = form_address.save()
                
                user.save()

                for tool in user_home_tools:
                    tool.location = user.address
                    tool.save()
                    
                if existent_shed:
                    user_shed_tools = models.Tool.objects.all().filter(location=shed.address)
                    
                    try:
                        new_shed_to_user = models.Shed.objects.get(address__zip_code=user.address.zip_code)
                            
                        for tool in user_shed_tools:
                            if tool.location == existent_shed.address:
                                tool.location = new_shed_to_user.address
                                
                                tool.save()
                                
                    except:
                        pass
                        
                messages.success(request, 'You have successfully updated your information')
                
                prev_user_address.delete()

                delete_me_from_statistics(user)

                return HttpResponseRedirect('/user_profile')

            else:
                form_address.set_state(form_address.cleaned_data['state'])

                prev_user_address = user.address
                user.address = form_address.save()
                
                user.save()

                for tool in user_home_tools:
                    tool.location = user.address
                    tool.save()

                messages.success(request, 'You have successfully updated your information')
                
                prev_user_address.delete()
                
                return HttpResponseRedirect('/user_profile')

    return render(request, 'manage_account.html', context)

# end manage_account function



# --------------------------------------
# function that cleans up the statistics
# --------------------------------------
def delete_me_from_statistics(user):
    me = models.DataStatistics.objects.all().filter(requester=user)
    me_again = models.DataStatistics.objects.all().filter(tool_requested__owner=user)

    for m in me:
        m.delete()

    for m in me_again:
        m.delete()

# end delete_me_from_statistics


# -----------------------------------------------
# do I have a tool that it has not been returned?
# -----------------------------------------------
def verify_borrowed_tools(user):
    try:
        borrowed_tools = models.CurrentlyBorrowedTools.objects.all().filter(possesor=user)

        if len(borrowed_tools) > 0:
            return False

        return True
    except:
        pass

# end verify_borrowed_tools function


# ----------------------------------------------------------------
# function that verifies the status of tools when leaving the shed
# ----------------------------------------------------------------
def verify_tool_status(user):
    try:
        if len(models.CurrentlyBorrowedTools.objects.all().filter(tool__owner=user)) == 0:
            return True

        else:
            return False
    except:
        pass

# end verify_tool_status function


# ------------------------------------
# function that verifies tool requests
# ------------------------------------
def verify_tool_requests(user):
    try:
        requests = models.ToolBorrowingRequest.objects.all().filter(tool_requested__owner=user)

        if len(requests) > 0:
            for request in requests:
                notification = models.Notification(notification_request_type='R',
                                                   notification_receiver=request.requester,
                                                   notification_information='USER MOVING FROM SHARE ZONE - TOOL REQUEST REJECTED',
                                                   notification_tool=request.tool_requested)
                notification.save()

                request.delete()
    except:
        pass

# end verify_tool_status function


# --------------------------------------------------
# function that process the selection of a new admin
# --------------------------------------------------
def select_admin(request):
    if not request.session['is_open']:
        return HttpResponseRedirect('/')

    user = get_user.get_user(request)

    users = models.User.objects.all().filter(address__zip_code = user.address.zip_code,
                                             admin = False).exclude(email= user.email)

    context = {
        'users' : users,
        'select_admin_page': True,
        'tool_requested_number': tool_requested.tool_requested(user),
        'num_notification': notification_num.notification_num(user),

    }

    context.update(add_context_extra_data.add_context_extra_data(user))

    return render(request, 'select_admin.html', context)

# end select_admin function


# -----------------------------------
# function that makes a user an admin
# -----------------------------------
def make_user_admin(request, user_id):
    if not request.session['is_open']:
        return HttpResponseRedirect('/')

    user = models.User.objects.get(id=user_id)

    user_using_sys = get_user.get_user(request)

    notification_sender = user_using_sys.first_name + ' ' + user_using_sys.last_name + ' (' +user_using_sys.email + ')'

    print(notification_sender)

    user.admin = True

    user.save()

    notification = models.Notification(notification_request_type='M',
                                       notification_receiver=user,
                                       notification_sender=notification_sender,
                                       notification_information='You have been promoted to an shed admin position')

    notification.save()

    messages.success(request, 'You have successfully selected '+ user.first_name + " " + user.last_name + ' (' + user.email + ') as an admin' )

    return HttpResponseRedirect('/user_profile/select_admin')

# end make_user_admin function