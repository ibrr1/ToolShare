from tool_share_app import models
from django.shortcuts import render
from django.http import HttpResponseRedirect
from tool_share_app.views import add_context_extra_data
# from django.contrib import messages
from tool_share_app.forms import search_form
# from django.db.models import Q

from . import tool_requested, notification_num


# --------------------------------
# function that searches for tools
# --------------------------------
def search(request):
    if not request.session['is_open']:
        return HttpResponseRedirect('/')

    user = models.User.objects.get(email=request.session['user_email'])

    searchForm = search_form.SearchForm(request.POST or None)

    context = {
        'search_page': True,
        'search_form': searchForm,
        'tool_requested_number': tool_requested.tool_requested(user),
        'num_notification': notification_num.notification_num(user),
    }

    context.update(add_context_extra_data.add_context_extra_data(user))

    if searchForm.is_valid():
        inputText = searchForm.cleaned_data['text']
        tool_condition = searchForm.cleaned_data['condition']
        tool_category = searchForm.cleaned_data['category']
        tool_location = searchForm.cleaned_data['tool_location']

        if tool_category == None:
            tool_category =''
        else:
            tool_category = tool_category.category

        shed = models.Shed.objects.get(address__zip_code = user.address.zip_code)

        if tool_location == 'home':
            tools_home = models.Tool.objects.all().filter(location=shed.address)

            tools = models.Tool.objects.all().filter(location__zip_code=user.address.zip_code,
                                                        name__contains=inputText,
                                                        condition__contains=tool_condition,
                                                        category__category__contains=tool_category,
                                                        activate = 'Activate'
                                                    )
            filtered_tools = []

            for tool in tools:
                if tool.location != shed.address:
                    filtered_tools.append(tool)

            tools = filtered_tools

        elif tool_location == 'shed':
            tools = models.Tool.objects.all().filter(location=shed.address, name__contains=inputText,
                                                        condition__contains=tool_condition,
                                                        category__category__contains=tool_category,
                                                         activate = 'Activate')

        else:
            tools = models.Tool.objects.all().filter(location__zip_code=user.address.zip_code,
                                                        name__contains=inputText,
                                                        condition__contains=tool_condition,
                                                        category__category__contains=tool_category,
                                                        activate = 'Activate')

        context = {
            'not_found': True,
            'search_page': True,
            'search_form': searchForm,
            'queryset': tools,

            'condition': tool_condition,
            'category': tool_category,

            'tool_owner': user.email,
            'hide_search_table': False,
            'hide_user_detail': True,
            'tool_requested_number': tool_requested.tool_requested(user),
            'num_notification': notification_num.notification_num(user),
        }

        if not tools:
            context['found'] = False

        context.update(add_context_extra_data.add_context_extra_data(user))

        # return render(request, 'search.html', context)


    return render(request, 'search.html', context)


# end search function
