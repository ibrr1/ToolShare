from django.http import HttpResponseRedirect
from tool_share_app import models
from django.contrib import messages
from django.shortcuts import render

from . import tool_requested, notification_num


def accept_requested_tool(request, tool_id):
	if not request.session['is_open']:
		return HttpResponseRedirect('/')

	user = models.User.objects.get(email=request.session['user_email'])

	try:
		tool = models.ToolBorrowingRequest.objects.get(tool_requested__id=tool_id)

		data_statistics = models.DataStatistics.objects.all()

		for data_statistic in data_statistics:
			print(data_statistic.requester.email + " " + user.email)

			if data_statistic.is_accepted == False and data_statistic.tool_requested == tool.tool_requested and tool.requester == data_statistic.requester:
				data_statistic.is_accepted = True
				data_statistic.save()

				break

		real_tool = models.Tool.objects.get(id=tool_id)
	
		real_tool.status = 'Unavailable'

		real_tool.save()
		
		context = {
			'receiver': tool.requester.first_name + ' ' + tool.requester.last_name + ' (' + tool.requester.email + ')',
			'tool_request_rejected': tool.tool_requested.name,
			'user_first_name': user.first_name,
			'tool_requested_number': tool_requested.tool_requested(user),
			'num_notification': notification_num.notification_num(user),
		}
		
		borrowed_tool = models.CurrentlyBorrowedTools(possesor=tool.requester, 
													tool=tool.tool_requested, 
													start_time=tool.date_request, 
													return_time=tool.date_return)
		borrowed_tool.save()
		
		notification = models.Notification(notification_request_type='A', 
										notification_receiver=tool.requester, 
										notification_information='Tool request accepted',
										notification_tool=tool.tool_requested)

		notification.save()
		
		messages.success(request, 'Request accepted. Notification sent to ' + tool.requester.first_name + ' ' + tool.requester.last_name + ' (' + tool.requester.email + ')')

		tool.delete()

	except:
	
		messages.warning(request, 'User cancelled request before being accepted or rejected, the transaction has been avoided.')
			
	return HttpResponseRedirect('/incoming_tool_requests/')