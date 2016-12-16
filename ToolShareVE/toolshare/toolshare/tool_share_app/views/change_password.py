from django.http import HttpResponseRedirect

from tool_share_app import models
from tool_share_app.forms.change_password_form import ChangePassword
from django.views.decorators.csrf import csrf_exempt
from tool_share_app.views import add_context_extra_data

from django.contrib import messages
from django.shortcuts import render

from . import tool_requested, notification_num, get_user


# ----------------------------------
# function that changes the password
# ----------------------------------
@csrf_exempt
def change_password(request):
	if not request.session['is_open']:
		return HttpResponseRedirect('/')
	
	user =get_user.get_user(request)
	change_password_form = ChangePassword(request.POST or None)
	
	context = {
		'change_password_form': change_password_form,
       	'tool_requested_number': tool_requested.tool_requested(user),
		'num_notification': notification_num.notification_num(user),
	}
	
	context.update(add_context_extra_data.add_context_extra_data(user))
	
	if change_password_form.is_valid():
		current_password = user.password
		
		if current_password == change_password_form.cleaned_data['current_password']:
			user.password = change_password_form.cleaned_data['new_password']
			user.save()
			
		else:
			messages.error(request, 'Invalid current password provided')
			return render(request, 'change_password.html', context)
		
		messages.success(request, 'Password updated successfully')
		return HttpResponseRedirect('/user_profile')
		
	return render(request, 'change_password.html', context)
	
# end change_password function