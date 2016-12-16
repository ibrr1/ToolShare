from tool_share_app import models
from tool_share_app.views import add_context_extra_data
from django.shortcuts import render

from . import tool_requested, notification_num


def tool_profile(request, tool_id):
    if not request.session['is_open']:
        return HttpResponseRedirect('/')
        
    shed_name = None
    user = models.User.objects.get(email=request.session['user_email'])
    tool = models.Tool.objects.get(id=tool_id)
    shed_address = None
    owner = False
    shed_corrdinators = []
    
    for single_user in models.User.objects.all():
        if single_user.admin == True and single_user.address.zip_code == user.address.zip_code:
            shed_corrdinators.append(single_user.first_name + " " + single_user.last_name + " (" + single_user.email + ")")

    for shed in models.Shed.objects.all():
        if shed.address.zip_code == user.address.zip_code:
            shed_address = shed.address
            break

    try:
        borrow_tool = models.CurrentlyBorrowedTools.objects.get(tool = tool)

        if borrow_tool.possesor == user:
            owner = True
    except:
        pass

    context = {
        'manage_tools': True,
        'current_user' : user,
        'tool_id': tool.id,
        'tool_name': tool.name,
        'tool_description': tool.description,
        'tool_category': tool.category,
        'tool_condition': tool.condition,
        'tool_location': tool.location,
        'tool_status': tool.status,
        'tool_owner': tool.owner,
        'owner_first_name': tool.owner.first_name,
        'owner_last_nmae': tool.owner.last_name,
        'owner_email': tool.owner.email,
        'owner_address': tool.owner.address,
        'tool_requested_number': tool_requested.tool_requested(user),
        'shed_coordinators': shed_corrdinators,
        'shed_address': shed_address,
        'num_notification': notification_num.notification_num(user),
        'is_owner' : owner,
    }

    context.update(add_context_extra_data.add_context_extra_data(user))

    return render(request, 'tool_profile.html', context)