from tool_share_app import models

# ------------------------------------
# function dedicated to the generation
# of the current user
# ------------------------------------
def get_user(request):
    return models.User.objects.get(email=request.session['user_email'])

# end get_user
