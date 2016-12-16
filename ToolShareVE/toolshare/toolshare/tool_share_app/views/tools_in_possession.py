from django.http import HttpResponseRedirect
from tool_share_app import models
from tool_share_app.views import add_context_extra_data
from django.shortcuts import render

from . import tool_requested, notification_num, get_user


# ----------------------------
# process the tools a user has
# ----------------------------
def tools_in_possession(request):
	if not request.session['is_open']:
		return HttpResponseRedirect('/')
		
	user = get_user.get_user(request)
	
	tools = models.CurrentlyBorrowedTools.objects.all().filter(possesor=user)
	
	context = {
		'tools_in_possession': tools,
		'tool_requested_number': tool_requested.tool_requested(user),
       	'num_notification': notification_num.notification_num(user),
	}
	
	context.update(add_context_extra_data.add_context_extra_data(user))
	
	return render(request, 'tools_in_possession.html', context)
	
# end tools_in_possession function