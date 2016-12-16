from tool_share_app import models
from tool_share_app.forms import update_tool_form
from django.shortcuts import render
from django.http import HttpResponseRedirect
from tool_share_app.views import add_context_extra_data
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from . import tool_requested, notification_num, get_user

# ---------------------------
# function that updates tools
# ---------------------------
@csrf_exempt
def update_tool(request, tool_id):
    if not request.session['is_open']:
        return HttpResponseRedirect('/')
        
    user = get_user.get_user(request)
    
    tool = models.Tool.objects.get(id=tool_id)
    
    if tool.location == user.address:
        tool_location = 'N'
    else:
        tool_location = 'Y'

    if tool.condition == 'Excellent':
        tool_condition = 'E'
    elif tool.condition == 'Good':
        tool_condition = 'G'
    else:
        tool_condition = 'R'

    if tool.status == 'Available':
        tool_status = 'Available'
    else:
        tool_status = 'Unavailable'

    if tool.activate == 'Activate':
        tool_activate = 'Activate'
    else:
        tool_activate = 'Deactivate'
        
    initial_form_data = {
            'name': tool.name,
            'description': tool.description,
            'category': tool.category.id,
            'condition': tool_condition,
            'in_shed': tool_location,
            'status': tool_status,
            'activate': tool_activate,
    }
        
    if request.method == 'GET':
        tool_form = update_tool_form.UpdateTool(initial_form_data or None)
        tool_form2 = update_tool_form.UpdateTool2(initial_form_data, user=models.User.objects.get(email=request.session['user_email']) or None)

        context = {
            'tool_form': tool_form,
            'tool_form2': tool_form2,
            'num_notification': notification_num.notification_num(user),
        }

        context.update(add_context_extra_data.add_context_extra_data(user))
        

    if request.method == 'POST':
        tool_form = update_tool_form.UpdateTool(request.POST or None)
        tool_form2 = update_tool_form.UpdateTool2(request.POST or None, user=models.User.objects.get(email=request.session['user_email']))

        context = {
            'tool_form': tool_form,
            'tool_form2': tool_form2,
            'num_notification': notification_num.notification_num(user),
        }

        context.update(add_context_extra_data.add_context_extra_data(user))

        if tool_form.is_valid() and tool_form2.is_valid():
            tool_name = tool_form.cleaned_data['name']
            tool_condition = tool_form2.cleaned_data['condition']
            tool_description = tool_form.cleaned_data['description']
            tool_category = tool_form.cleaned_data['category']
            is_in_shed = tool_form2.cleaned_data['in_shed']
            tool_status = tool_form2.cleaned_data['status']
            tool_activate = tool_form2.cleaned_data['activate']
            
            if tool.status == 'Unavailable' and tool_status == 'Available':
                if len(models.CurrentlyBorrowedTools.objects.all().filter(tool=tool)) > 0:
                    messages.error(request, 'This tool "'+ tool.name + '" has been borrowed by another user! it cannot be available until it is returned')
        
                    return HttpResponseRedirect('/user_profile/manage_tools/sdf/update_tool/' + tool_id + '/')
                    

            if is_in_shed == 'N':
                tool.location = user.address

            if is_in_shed == 'Y':
                sheds = models.Shed.objects.all()
            
                for shed in sheds:
                    if shed.address.zip_code == user.address.zip_code:
                        tool.location = shed.address
                        break
                
            if tool_category:
                tool.category = models.ToolCategory.objects.get(category=tool_category)

            if tool_condition == 'E':
                tool.condition = 'Excellent'

            elif tool_condition == 'G':
                tool.condition = 'Good'

            else:
                tool.condition = 'Regular'

            tool.status = tool_status  
            tool.activate = tool_activate 
            tool.name = tool_name
            tool.description = tool_description
            tool.save()

            messages.success(request, "You have successfully updated your tool")

            return HttpResponseRedirect('/user_profile/manage_tools/all_tools/share_zone_tools/')

    context['tool_requested_number'] = tool_requested.tool_requested(user)
    
    return render(request, 'update_tool.html', context)
    
# end update_tool_form function