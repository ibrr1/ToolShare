from tool_share_app import models
from django.shortcuts import render
from django.http import HttpResponseRedirect
from tool_share_app.views import add_context_extra_data

from . import tool_requested, notification_num


def requested_tools(request):
	if not request.session['is_open']:
		return HttpResponseRedirect('/')
	
	user = models.User.objects.get(email=request.session['user_email'])
	
	user_requested_tools = models.ToolBorrowingRequest.objects.all()
	
	requested_tools = []
	
	for tool in user_requested_tools:
		if tool.requester == user:
			requested_tools.append(tool.tool_requested)
			
	context = {
		'requested_tools': requested_tools,
		'tool_requested_number': tool_requested.tool_requested(user),
        'num_notification': notification_num.notification_num(user),
	}
	
	context.update(add_context_extra_data.add_context_extra_data(user))

	return render(request, 'requested_tools.html', context)