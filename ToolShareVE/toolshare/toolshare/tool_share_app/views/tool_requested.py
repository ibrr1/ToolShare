from tool_share_app import models

# ---------------------------------------
# calculates the number of tool_requested
# ---------------------------------------
def tool_requested(user):
	found = False
	shed = None
	tools = []
 	
	if user.admin == True:		
		try:
			shed = models.Shed.objects.get(address__zip_code=user.address.zip_code)
		
		except:
			return 0
		
		shed_tools = models.ToolBorrowingRequest.objects.all()
		admin_tools = models.ToolBorrowingRequest.objects.all().filter(tool_requested__owner=user)
		
		for admin_tool in admin_tools:
			for tool in shed_tools:
				if admin_tool == tool:
					
					found = True	
			
			if not found:
				shed_tools.append(admin_tool)
				
			else:
				found = False
				
			tools = shed_tools
			
	else:		
		try:
			shed = models.Shed.objects.get(address__zip_code=user.address.zip_code)

		except:
			return 0

		user_tools = models.ToolBorrowingRequest.objects.all().filter(tool_requested__owner=user)
		
		for tool in user_tools:
			if tool.tool_requested.location == shed.address:
				found = True
				
			if not found:
				tools.append(tool)
			
			else:
				found = False
				
	return len(tools)
	
# end tool_requested function