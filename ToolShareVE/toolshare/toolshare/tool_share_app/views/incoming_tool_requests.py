from django.http import HttpResponseRedirect
from tool_share_app import models
from tool_share_app.forms import login_form
from tool_share_app.views import add_context_extra_data
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

import textwrap
from django.contrib import messages

from . import tool_requested, notification_num



# ------------------------------
# manages incoming tool requests
# ------------------------------
@csrf_exempt
def incoming_tool_requests(request):
	if not request.session['is_open']:
		return HttpResponseRedirect('/')

	found = False
	user = models.User.objects.get(email=request.session['user_email'])
	shed = models.Shed.objects.get(address__zip_code=user.address.zip_code)


	if user.admin:
		tools = models.ToolBorrowingRequest.objects.all()

		for admin_tool in models.ToolBorrowingRequest.objects.all().filter(tool_requested__owner=user):
			for tool in tools:
				if admin_tool == tool:
					found = True

			if not found:
				tools.append(admin_tool)

			else:
				found = False

	else: # not an admin
		tools = []

		for tool in models.ToolBorrowingRequest.objects.all().filter(tool_requested__owner=user):
			if tool.tool_requested.location == shed.address:
				found = True

			if not found:
				tools.append(tool)

			else:
				found = False

	context = {
		'requested_tools': tools,
		'tool_requested_number': tool_requested.tool_requested(user),
		'num_notification': notification_num.notification_num(user),
		'Tool_Requested_page': True
	}

	context.update(add_context_extra_data.add_context_extra_data(user))

	return render(request, 'incoming_tool_requests.html', context)

# end incoming_tool_requests function