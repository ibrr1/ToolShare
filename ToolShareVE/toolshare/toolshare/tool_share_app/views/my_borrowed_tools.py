from django.http import HttpResponseRedirect
from tool_share_app import models
from django.contrib import messages
from django.shortcuts import render
from tool_share_app import models

import re

from . import tool_requested, notification_num, add_context_extra_data


def my_borrowed_tools(user):
	counter = 0

	for currently_borrowed_tool in models.CurrentlyBorrowedTools.objects.all():
		if currently_borrowed_tool.possesor == user and currently_borrowed_tool.flag == False:
			counter = counter + 1

	return counter


def borrowed_tools(request):
	if not request.session['is_open']:
  		return HttpResponseRedirect('/')

	borrowed_tools = []

	user = models.User.objects.get(email=request.session['user_email'])

	for currently_borrowed_tool in models.CurrentlyBorrowedTools.objects.all():
		if currently_borrowed_tool.possesor == user and currently_borrowed_tool.flag == False:
			borrowed_tools.append(currently_borrowed_tool)

	context = {
		'borrowed_tools': borrowed_tools,
		'tool_requested_number': tool_requested.tool_requested(user),
		'num_notification': notification_num.notification_num(user),
	}

	context.update(add_context_extra_data.add_context_extra_data(user))

	return render(request, 'my_borrowed_tools.html', context)


def returned_tool(request, tool_id):
	if not request.session['is_open']:
  		return HttpResponseRedirect('/')

	user = models.User.objects.get(email=request.session['user_email']);

	returned_tool = models.CurrentlyBorrowedTools.objects.get(tool__id=tool_id)

	if user.admin == True and returned_tool.tool.location == models.Shed.objects.get(address__zip_code=user.address.zip_code).address:
		tool = models.Tool.objects.get(id=returned_tool.tool.id)

		returned_tool.delete()

		tool.status = 'Available'

		tool.save()

	else:
		notification = models.Notification(notification_request_type='C',
										   notification_receiver=returned_tool.tool.owner,
										   notification_sender=user.first_name + ' ' + user.last_name + \
																	' (' + user.email + ')',

										   notification_information='Tool \' ' + returned_tool.tool.name + ' \' marked as returned.',
										   notification_tool=returned_tool.tool)

		notification.save()

		returned_tool.flag = True

		returned_tool.save()

	return HttpResponseRedirect('/user_profile/my_borrowed_tools')


def confirm_return(request, tool_id):
	user = models.User.objects.get(email=request.session['user_email'])

	tool = models.Tool.objects.get(id=tool_id)

	my_notification = models.Notification.objects.get(notification_tool=tool, notification_request_type='C')

	tool_returned = models.CurrentlyBorrowedTools.objects.get(tool__id=tool_id)

	tool.status = 'Available'

	tool.save()

	notification = models.Notification(notification_request_type='M',
									   notification_receiver=tool_returned.possesor,
									   notification_information='Tool owner confirmed the return of the tool ' + tool.name,
									   notification_tool=tool)

	notification.save()

	my_notification.delete()

	tool_returned.delete()

	return HttpResponseRedirect('/notifications')


def reject_return(request, tool_id):
	tool = models.Tool.objects.get(id=tool_id)

	returned_tool = models.CurrentlyBorrowedTools.objects.get(tool__id=tool_id)

	user = models.User.objects.get(email=request.session['user_email'])

	prev_notification = models.Notification.objects.get(notification_tool=tool, notification_request_type='C')

	prev_email = prev_notification.notification_sender.split()

	email = prev_email[-1][1:-1]

	receiver = models.User.objects.get(email__contains=email)

	notification = models.Notification(notification_request_type='M',
									   notification_sender=user.first_name + ' ' + user.last_name + ' (' + user.email + ')',
									   notification_receiver=receiver,
									   notification_information='Tool return has been rejected, please contact tool\'s owner or possessor',
									   notification_tool=tool)

	notification.save()

	prev_notification.delete()

	returned_tool.flag = False

	returned_tool.save()

	return HttpResponseRedirect('/notifications')
