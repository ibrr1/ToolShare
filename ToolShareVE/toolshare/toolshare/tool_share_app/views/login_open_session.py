from django.http import HttpResponseRedirect

# ---------------
# opens a session
# ---------------
def login_open_session(request, email):
    request.session['is_open'] = True
    request.session['user_email'] = email

    return HttpResponseRedirect('/user_profile')
    
# end login_open_session function