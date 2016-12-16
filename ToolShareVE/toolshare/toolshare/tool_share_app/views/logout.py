from django.http import HttpResponseRedirect


# -----------------------------
# functions that logs out users
# -----------------------------
def logout(request):
    request.session['is_open'] = False 
    request.session['shed_created'] = False
    
    return HttpResponseRedirect('/')
    
# end logout function