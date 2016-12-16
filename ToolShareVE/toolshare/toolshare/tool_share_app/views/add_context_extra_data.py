from tool_share_app import models

# ---------------------------------------
# this function adds the shed information
# ---------------------------------------
def add_context_extra_data(user):
    sheds = models.Shed.objects.all()
    
    context = {
        'user': user,
        'zip_code': user.address.zip_code,
        'user_type': 'Admin' if user.admin == True else 'User',
    }
    
    for shed in sheds:
        if shed.address.zip_code == context['zip_code']:
            context['shed_name'] = shed.name
            context['shed_address'] = shed.address
            
            break
            
    return context