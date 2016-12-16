from tool_share_app import models, forms
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render
from tool_share_app.forms.date_form import RequestDate, ReturnDate
from tool_share_app.views import add_context_extra_data
from django.views.decorators.csrf import csrf_exempt

import datetime, calendar

from . import tool_requested, notification_num


# ---------------------
# process tool requests
# ---------------------
@csrf_exempt
def tool_request(request, tool_id, tool_listing_section):
	if not request.session['is_open']:
		return HttpResponseRedirect('/')
	
	try:
		tool = models.Tool.objects.get(id=tool_id)
	
	except:
		messages.warning(request, 'Tool requested has been deleted from the system, the transaction could not be completed')
		
		return HttpResponseRedirect('/user_profile/manage_tools/all_tools/')
		
	if tool.status == 'Unavailable':
		messages.error(request, 'This tool "'+ tool.name + '" is unavailable! it cannot be requested')
		
		return HttpResponseRedirect('/user_profile/manage_tools/all_tools/' + tool_listing_section)

	user = models.User.objects.get(email=request.session['user_email'])
	request_date_form = RequestDate(request.POST or None)
	return_date_form = ReturnDate(request.POST or None)
	shed = models.Shed.objects.get(address__zip_code=user.address.zip_code)

	context = {
		'tool_requested_number': tool_requested.tool_requested(user),
		'email': user.email,
		'address': user.address,
		'num_notification': notification_num.notification_num(user),
		'request_date_form': request_date_form, 
		'return_date_form': return_date_form, 
		'tool_requested': tool,
	}
	
	context.update(add_context_extra_data.add_context_extra_data(user))

	if request_date_form.is_valid() and return_date_form.is_valid():

		data_statistics = models.DataStatistics()

		if tool.location == shed.address and user.admin == True:
			tool_borrowed = models.CurrentlyBorrowedTools(possesor=user,
														  tool=tool,
													 	  start_time=request_date_form.cleaned_data['start_date'],
														  return_time=return_date_form.cleaned_data['return_date'])
			tool.status = 'Unavailable'

			tool.save()

			tool_borrowed.save()

			data_statistics.tool_requested = tool

			data_statistics.requester = user

			data_statistics.is_accepted =True

			data_statistics.save()

			messages.success(request, 'You have successfully obtained "'+ tool.name + '"')

			return HttpResponseRedirect('/user_profile/manage_tools/all_tools/' + tool_listing_section)


		if tool.location == shed.address:
			tool_borrowed = models.CurrentlyBorrowedTools(possesor=user, 
														  tool=tool, 
													 	  start_time=request_date_form.cleaned_data['start_date'], 
														  return_time=return_date_form.cleaned_data['return_date'])

			# class Notification(models.Model):
    			# notification_request_type = models.CharField(max_length=1)
    			# notification_receiver = models.ForeignKey(User)
    			# notification_sender = models.CharField(max_length=100, default='')
    			# notification_information = models.CharField(max_length=256)
    			# notification_tool = models.ForeignKey(Tool, blank=True, null=True)
    			# notification_timestamp = models.DateTimeField(default=datetime.datetime.now)

			shed_coordinator = models.User.objects.get(address__zip_code=user.address.zip_code, admin=True)

			print(user.first_name)

			notification = models.Notification(notification_request_type='Z',
											   notification_receiver=shed_coordinator,
											   notification_sender=user.first_name + ' ' + user.last_name + \
											   ' (' + user.email + ')',
											   notification_information="'" + tool_borrowed.tool.name + "' borrowed from shed.",
											   notification_tool=tool_borrowed.tool)

			notification.save()

			tool.status = 'Unavailable'

			tool.save()

			tool_borrowed.save()

			data_statistics.tool_requested = tool

			data_statistics.requester = user

			data_statistics.is_accepted =True

			data_statistics.save()

			messages.success(request, 'You have successfully obtained "'+ tool.name + '"')
			
			return HttpResponseRedirect('/user_profile/manage_tools/all_tools/' + tool_listing_section)
		
		else:
			tool_being_requested = models.ToolBorrowingRequest(requester=user, 
														date_request=request_date_form.cleaned_data['start_date'], 
														date_return=return_date_form.cleaned_data['return_date'], 
														tool_requested=tool)
			
			if datetime.date.today() > request_date_form.cleaned_data['start_date']:
				
				date = str(request_date_form.cleaned_data['start_date'])
				
				messages.error(request, 'Invalid date start date '+ str(datetime.date(1900, int(date[5:7]), 1).strftime('%B')) + ',' + date[8:] +',' + date[0:4] + '! The date must start from today\'s date')
				
				return HttpResponseRedirect('/user_profile/manage_tools/all_tools/share_zone_tools/request/'+ tool_id +'/')
			
			if request_date_form.cleaned_data['start_date'] > return_date_form.cleaned_data['return_date']:
				
				date = str(return_date_form.cleaned_data['return_date'])
				
				messages.error(request, 'Invalid date return date '+ str(datetime.date(1900, int(date[5:7]), 1).strftime('%B')) + ',' + date[8:] +',' + date[0:4] + '! The date must start from the start\'s date')
				
				return HttpResponseRedirect('/user_profile/manage_tools/all_tools/share_zone_tools/request/'+ tool_id +'/')
			
			tool_being_requested.save()

			data_statistics.tool_requested = tool

			data_statistics.requester = user

			data_statistics.save()
		
			messages.success(request, 'You have successfully requested "'+ tool.name + '". Your tool requests can be seen under the My requested tools tab.')
		
			return HttpResponseRedirect('/user_profile/manage_tools/all_tools/' + tool_listing_section)
		
	return render(request, 'tools_usage_dates.html', context)
	
# end tool_request function