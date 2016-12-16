from django.shortcuts import render
from django.db.models import Count
from django.http import HttpResponseRedirect

from tool_share_app import models

from . import tool_requested, notification_num, get_user, add_context_extra_data


# ------------------------------------
# function dedicated to the generation 
# of community shed statistics
# ------------------------------------
def user_statistics(type, user):
    def_statistics_size = 5
    
    return {
        'most_used_tools': models.DataStatistics.objects.values('tool_requested__name', 'tool_requested__id',
                                                                'tool_requested__owner__first_name', 
                                                                'tool_requested__owner__last_name',
                                                                'tool_requested__owner__email',
                                                                'tool_requested__owner__address__street_address',
                                                                'tool_requested__owner__address__city',
                                                                'tool_requested__owner__address__zip_code',
                                                                'tool_requested__owner__admin').filter(tool_requested__location__in=models.Address.objects.filter(zip_code=user.address.zip_code),
                                                                                                       is_accepted=True).annotate(Count('tool_requested')).order_by('-tool_requested__count')[:def_statistics_size],
    
        'most_active_borrowers': models.DataStatistics.objects.values('requester__first_name',
                                                                 'requester__last_name',
                                                                 'requester__address__street_address',
                                                                 'requester__address__city',
                                                                 'requester__address__zip_code',
                                                                 'requester__email',
                                                                 'requester__admin',
                                                                 'requester__last_name',).filter(tool_requested__location__in=models.Address.objects.filter(zip_code=user.address.zip_code),
                                                                                                 is_accepted=True).annotate(Count('requester')).order_by('-requester__count')[:def_statistics_size],
                                                                 
        'most_active_lenders': models.DataStatistics.objects.values('tool_requested__owner',
                                                               'tool_requested__owner__first_name',
                                                               'tool_requested__owner__last_name',
                                                               'tool_requested__owner__email',
                                                               'tool_requested__owner__address__street_address',
                                                               'tool_requested__owner__address__city',
                                                               'tool_requested__owner__address__zip_code',
                                                               'tool_requested__owner__admin').filter(tool_requested__location__in=models.Address.objects.filter(zip_code=user.address.zip_code),
                                                                                                      is_accepted=True).annotate(Count('tool_requested__owner_id')).order_by('-tool_requested__owner_id__count')[:def_statistics_size],
        
        'most_recently_used_tools': models.DataStatistics.objects.values('tool_requested__name',
                                                                    'tool_requested__location__street_address',
                                                                    'tool_requested__location__city',
                                                                    'tool_requested__location__zip_code',
                                                                    'tool_requested__category__category',
                                                                    'tool_requested__owner__first_name',
                                                                    'tool_requested__owner__last_name',
                                                                    'tool_requested__id').filter(tool_requested__location__in=models.Address.objects.filter(zip_code=user.address.zip_code),
                                                                                                 is_accepted=True).order_by('-id').distinct()[:def_statistics_size],
    }[type]
    
# end user_statistics
    

# --------------------------------------------
# helps in filtering and eliminating duplicate
# values from the most_recently_used_tools
# --------------------------------------------
def filter_most_recently_used_tools(user):
    try:
        different = True

        filtered_most_recently_used_tools = []

        most_recently_used_tools = user_statistics('most_recently_used_tools', user)

        filtered_most_recently_used_tools.append(most_recently_used_tools[0])

        for value in user_statistics('most_recently_used_tools', user):
            for filtered_most_recently_used_tool in filtered_most_recently_used_tools:
                if value == filtered_most_recently_used_tool:
                    different = False


            if different:
                filtered_most_recently_used_tools.append(value)

            else:
                different = True
                
        return filtered_most_recently_used_tools
        
    except:
        pass

# end filter_most_recently_used_tools function


# ----------------------------------------
# function that gets the shed coordinators
# ----------------------------------------
def get_shed_coordinators(zip_code):
    shed_coordinators = []

    for single_user in models.User.objects.all():
        if single_user.admin == True and single_user.address.zip_code == zip_code:
            shed_coordinators.append(single_user.first_name + " " + single_user.last_name + " (" + single_user.email + ")")

    return shed_coordinators

# end get_shed_coordinators


# -------------------------------------
# function that generates local context
# -------------------------------------
def generate_local_context(user):
    return {
            'user_profile_page': True,
            'tool_requested_number': tool_requested.tool_requested(user),
            'shed_coordinators': get_shed_coordinators(user.address.zip_code),
            'num_notification': notification_num.notification_num(user),
            
            # statistics
            'most_used_tools': user_statistics('most_used_tools', user),
            'most_recently_used_tools': filter_most_recently_used_tools(user),
            
            'most_active_borrowers': user_statistics('most_active_borrowers', user),
            'most_active_lenders': user_statistics('most_active_lenders', user),
        }
        
# end generate_local_context function
 
 
# ---------------------------------------------------
# function that determines if there is a shed created
# ---------------------------------------------------
def determine_if_shed_created(context, request):
    sheds = models.Shed.objects.all()
    
    context['shed_name'] = None

    for shed in sheds:
        if shed.address.zip_code == context['zip_code']:
            context['shed_name'] = shed.name
            
            request.session['shed_created'] = True                     
            
            return True

    request.session['shed_created'] = False
    
    return False    
    
# end determine_if_shed_created function        
        
      
# ---------------------------------------
# function that displays and 
# generates content for the user profile
# ---------------------------------------
def user_profile(request):
    if not request.session['is_open']: # is user logged in?
        return HttpResponseRedirect('/')
    
    user = get_user.get_user(request)

    context = generate_local_context(user)
    
    context.update(add_context_extra_data.add_context_extra_data(user)) 
   
    if not determine_if_shed_created(context, request):
        return HttpResponseRedirect('/shed_creation')    
   
        
    return render(request, 'user_profile.html', context)