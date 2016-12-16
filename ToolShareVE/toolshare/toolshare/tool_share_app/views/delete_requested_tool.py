from django.http import HttpResponseRedirect
from tool_share_app import models
from django.contrib import messages


def delete_requested_tool(request, tool_id):
	if not request.session['is_open']:
		return HttpResponseRedirect('/')
	
	try:
		tool = models.ToolBorrowingRequest.objects.get(tool_requested__id=tool_id)
		tool.delete()
		
	except:
		pass
		
	return HttpResponseRedirect('/user_profile/requested_tools/')