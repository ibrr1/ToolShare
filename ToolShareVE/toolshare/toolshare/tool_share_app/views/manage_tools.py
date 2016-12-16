from tool_share_app import models
from tool_share_app.forms import add_tool_form, date_form
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import Count

from . import tool_requested, notification_num, my_borrowed_tools, get_user, add_context_extra_data


# ----------------------------------
# generates user personal statistics
# ----------------------------------
def user_statistics(user, type):
    def_statistics_size = 5

    return {'user_most_used_tools': models.DataStatistics.objects.values('tool_requested__name', 'tool_requested__id',
                                                                         'tool_requested__owner__first_name',
                                                                         'tool_requested__owner__last_name',
                                                                         'tool_requested__owner__email').filter(tool_requested__owner=user,
                                                                         is_accepted=True).annotate(Count('tool_requested')).order_by('-tool_requested__count')[:def_statistics_size],

            'user_most_borrowed_tools': models.DataStatistics.objects.values('tool_requested__name', 'tool_requested__id',
                                                                         'tool_requested__owner__first_name',
                                                                         'tool_requested__owner__last_name',
                                                                         'tool_requested__owner__email').filter(requester=user,
                                                                         is_accepted=True).annotate(Count('tool_requested')).order_by('-tool_requested__count')[:def_statistics_size],
    }[type]

# end user_statistics function


# ---------------------------------------------------------------
# function that updates tools when the user leaves the share zone
# ---------------------------------------------------------------
def update_user_shed_tools(context):
    user = context['user']
    user_shed = models.Shed.objects.get(address__zip_code=user.address.zip_code)

    for tool in models.Tool.objects.all().filter(owner=user):
        if tool.location.zip_code != user.address.zip_code:
            tool.location = user_shed.address

            tool.save()

    if user.admin == True:
        context['user_shed'] = user_shed
        
# end update_user_shed_tools function


# -------------------------------------------
# filtering actual tools with requested tools
# -------------------------------------------
def filter_tools_requested(tools, context, user):   
    found = False
    
    tools_queryset = []
    tools_filtered = []
    
    num_requested_tools = 0
    
    tools_requested = models.ToolBorrowingRequest.objects.all()

    for tool_o in models.Tool.objects.all():
        for tool_i in tools_requested:
            if tool_o == tool_i.tool_requested and tool_i.requester == user:
                num_requested_tools = num_requested_tools + 1
                tools_queryset.append(tool_o)

    for tool in tools:
        for t_requested in tools_requested:
            if tool == t_requested.tool_requested:
                found = True

        if not found:
            tools_filtered.append(tool)

        else:
            found = False
            
    context['queryset'] =  tools_filtered
    context['num_requested_tools'] = num_requested_tools
    context['tool_requested_number'] = tool_requested.tool_requested(user)

# end filter_tools_requested function


# ------------------------------------------------------
# determines if a tool has been added by a specific user
# ------------------------------------------------------
def tool_exists(user, tool_name):
    user_tools = models.Tool.objects.all().filter(owner=user);

    for tool in user_tools:
        if tool.name == tool_name:
            return True
            
    return False

# end tool_exists function


# -----------------------------------------------
# determines where the tool is goind to be stored
# -----------------------------------------------
def determine_tool_placement(is_in_shed, user):
    place = ''
    
    if is_in_shed == 'N':
        return user.address
            
    elif is_in_shed == 'Y':
        for shed in models.Shed.objects.all():
            if shed.address.zip_code == user.address.zip_code:
                return shed.address

# end determine_tool_placement function
    
    
# ----------------------------------
# determines the condition of a tool
# ----------------------------------
def determine_tool_condition(tool_condition):
    condition = ''

    if tool_condition == 'E':
        condition = 'Excellent'

    elif tool_condition == 'G':
        condition = 'Good'

    else:
        condition = 'Regular'
   
    return condition

# end determine_tool_condition function


# -------------------------------------
# manages the tool addition and listing
# -------------------------------------
@csrf_exempt
def manage_tools(request, tool_listing_type):
    if not request.session['is_open']:
        return HttpResponseRedirect('/')

    if not request.session['shed_created']:
        return HttpResponseRedirect('/shed_creation')

    tools = None
    
    user = get_user.get_user(request)

    date_form_request = date_form.RequestDate(request.POST or None)
    date_form_return = date_form.ReturnDate(request.POST or None)

    add_tool_form_imp = add_tool_form.ToolAggregator(request.POST or None, 
                                                 user=models.User.objects.get(email=user.email))

    context = {
        'manage_tools': True,
        'tool_form': add_tool_form_imp,
        'date_form_request': date_form_request,
        'date_form_return': date_form_return,
        'num_notification': notification_num.notification_num(user),
        'my_borrowed_tools': my_borrowed_tools.my_borrowed_tools(user),
        'user_most_used_tools': user_statistics(user, 'user_most_used_tools'),
        'user_most_borrowed_tools': user_statistics(user, 'user_most_borrowed_tools'),
        'shed': models.Shed.objects.get(address__zip_code=user.address.zip_code),
    }

    context.update(add_context_extra_data.add_context_extra_data(user))

    try:
        tools = tool_listing(tool_listing_type, user, context).order_by('id').reverse()
        
        update_user_shed_tools(context)
        
        filter_tools_requested(tools, context, user)

    except:
        pass

    if add_tool_form_imp.is_valid():
    
        tool_name = add_tool_form_imp.cleaned_data['name']
        tool_condition = add_tool_form_imp.cleaned_data['condition']
        tool_description = add_tool_form_imp.cleaned_data['description']
        tool_category = add_tool_form_imp.cleaned_data['category']
        is_in_shed = add_tool_form_imp.cleaned_data['in_shed']

        if tool_exists(user, tool_name):
            context['error'] = True
        
            messages.error(request, "Tool not added! Tool already registered by you")
            
            return render(request, 'manage_tools.html', context)

        new_tool = models.Tool(name=tool_name, 
                               condition=determine_tool_condition(tool_condition),
                               status='Available', 
                               activate='Activate', 
                               description=tool_description,
                               location=determine_tool_placement(is_in_shed, user),
                               category=models.ToolCategory.objects.get(category=tool_category),
                               owner=user)
                               
        new_tool.save()

        messages.success(request, "Tool added with the name of \"" + new_tool.name + "\".")

        return HttpResponseRedirect('/user_profile/manage_tools/' + tool_listing_type)

    elif not add_tool_form_imp.is_valid() and request.method == 'POST':
        context['error'] = True
        
        messages.error(request, "Tool not added! verify input form below to get more information about why the tool was not added")

    return render(request, 'manage_tools.html', context)

# end manage_tools function


# --------------------------------
# generates the tools to be listed
# --------------------------------
def tool_listing(listing_type, user, context):
    tools = models.Tool.objects.all()

    if listing_type == 'all_tools':
        context['all_tools'] = True
        
        return models.Tool.objects.all().filter(owner_id__exact=user.id).reverse()

    elif listing_type == 'all_tools/tools_shed':
        context['shed_tools'] = True
        sheds = models.Shed.objects.all()

        for shed in sheds:
            if shed.address.zip_code == user.address.zip_code:
                return models.Tool.objects.all().filter(location=shed.address, activate='Activate')

    elif listing_type == 'all_tools/share_zone_tools':
        context['zone_tools'] = True
        
        return models.Tool.objects.all().filter(location__in=models.Address.objects.filter(zip_code=user.address.zip_code), activate='Activate')

    else:
        context['home_tools'] = True
        
        return models.Tool.objects.all().filter(location=user.address)

# end tool_listing function


# ------------------------------------------------------------------
# redirects the user one an action has been performed over the tools
# ------------------------------------------------------------------
def redirect_user(tool_listing_type):
    if 'tools_shed' in tool_listing_type:
        return HttpResponseRedirect('/user_profile/manage_tools/all_tools/tools_shed/')

    elif 'home_tools' in tool_listing_type:
        return HttpResponseRedirect('/user_profile/manage_tools/all_tools/home_tools/')

    elif 'share_zone_tools' in tool_listing_type:
        return HttpResponseRedirect('/user_profile/manage_tools/all_tools/share_zone_tools/')

    elif 'search' in tool_listing_type:
        return HttpResponseRedirect('/user_profile/search/')
        
# end redirect_user function


# --------------
# deletes a tool
# --------------
def manage_tools_deletion(request, tool_listing_type, tool_id):
    if not request.session['is_open']:
        return HttpResponseRedirect('/')

    tool = models.Tool.objects.get(id=tool_id)

    if tool.status == 'Unavailable':
        messages.error(request, 'This tool "'+ tool.name + '" is unavailable! it cannot be deleted')

        return HttpResponseRedirect('/user_profile/manage_tools/all_tools/' + tool_listing_type)

    tool.delete()
    return redirect_user(tool_listing_type)

# end manage_tools_deletion function


# --------------
# deletes a tool
# --------------
def manage_tools_deletion_alt(request, tool_id):
    if not request.session['is_open']:
        return HttpResponseRedirect('/')

    tool = models.Tool.objects.get(id=tool_id)

    if tool.status == 'Unavailable':
        messages.error(request, 'This tool "'+ tool.name + '" is unavailable! it cannot be deleted')

        return HttpResponseRedirect('/user_profile/manage_tools/all_tools/')

    tool.delete()

    return HttpResponseRedirect('/user_profile/manage_tools/all_tools')

# end manage_tools_deletion_alt function