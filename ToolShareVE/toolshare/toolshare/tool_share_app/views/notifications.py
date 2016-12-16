from django.http import HttpResponseRedirect
from tool_share_app import models
from tool_share_app.views import add_context_extra_data
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import render

import datetime, textwrap

from . import tool_requested, notification_num, get_user


# ---------------------------------------------
# wraps the text to be printed in notifications
# ---------------------------------------------
@csrf_exempt
def text_wrap(notifications):
	for notification in notifications:
		if len(notification.notification_information) > 50:
			lines = textwrap.wrap(notification.notification_information, 50)
			notification.notification_information = ''
			
			for line in lines:
				notification.notification_information = notification.notification_information + line + '\n'
		
		notification.save()
		
	return notifications
	
# end text_wrap function


# ---------------------------
# function used to wrap names
# ---------------------------
# def text_wrap_name(notifications):
# 	for notification in notifications:
# 		if len(notification.notification_sender) > 15:
# 			lines = textwrap.wrap(notification.notification_sender, 15)
#
# 			notification.notification_sender = ''
#
# 			for line in lines:
# 				notification.notification_sender = notification.notification_sender + line + '\n'
#
# 		notification.save()
#
# 	return notifications

# end text_wrap_name

# -----------------------------------
# function that process notifications
# -----------------------------------
def notifications(request):
	if not request.session['is_open']:
  		return HttpResponseRedirect('/')
	
	user = get_user.get_user(request)
	
	notifications = models.Notification.objects.all().filter(notification_receiver__email=user.email).order_by('-id')
	
	context = {
		'user_first_name': user.first_name,
		'tool_requested_number': tool_requested.tool_requested(user),
		'num_notification': notification_num.notification_num(user),
		'notifications_exist': True if len(notifications) > 0 else False,
		'notifications': text_wrap(notifications),
		'notifications_page':True
	}
	
	context.update(add_context_extra_data.add_context_extra_data(user))
	
	return render(request, 'notifications.html', context)
	
# end notifications function


# -----------------------------------
# function that deletes notifications
# -----------------------------------
def delete_notification(request, notification_id):
	models.Notification.objects.get(id=notification_id).delete()
	
	return HttpResponseRedirect('/notifications/')

# end delete_notification function