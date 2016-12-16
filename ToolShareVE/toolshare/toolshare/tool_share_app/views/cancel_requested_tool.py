from django.http import HttpResponseRedirect
from tool_share_app import models
from tool_share_app.forms.notification import Notification
from django.views.decorators.csrf import csrf_exempt
from tool_share_app.views import add_context_extra_data
from django.contrib import messages
from django.shortcuts import render

from . import tool_requested, notification_num


@csrf_exempt
def cancel_requested_tool(request, tool_id):
	if not request.session['is_open']:
		return HttpResponseRedirect('/')
	
	notification_form = Notification(request.POST or None)

	user = models.User.objects.get(email=request.session['user_email'])
	
	context = {
		'notification_form': notification_form,
		'user_first_name': user.first_name,
		'tool_requested_number': tool_requested.tool_requested(user),
		'num_notification': notification_num.notification_num(user),
	}
	
	try:
		tool = models.ToolBorrowingRequest.objects.get(tool_requested__id=tool_id)
		
		context['receiver'] = tool.requester.first_name + ' ' + tool.requester.last_name + ' (' + tool.requester.email + ')'
		context['tool_request_rejected'] = tool.tool_requested
		
		context.update(add_context_extra_data.add_context_extra_data(user))
		
		if notification_form.is_valid():
			notification = notification_form.cleaned_data['message']
			
			notification_form.set_notification_type('R')
			notification_form.set_receiver(tool.requester)
			notification_form.set_sender(tool.tool_requested.owner.email)
			notification_form.set_tool(tool.tool_requested)
			notification_form.set_notification_information(notification)
			
			notification_form.save()
			
			messages.success(request, 'Request cancelled. Notification sent to ' + tool.requester.first_name + ' ' + tool.requester.last_name + ' (' + tool.requester.email + ')')
			
			tool.delete()
			
			return HttpResponseRedirect('/incoming_tool_requests/')
			
	except:
		messages.warning(request, 'User cancelled request before being accepted or rejected, the transaction has been avoided - incomplete')
	
		return HttpResponseRedirect('/incoming_tool_requests/')
			
	return render(request, 'cancel_requested_tool.html', context)