from tool_share_app import models

def notification_num(user):
	return len(models.Notification.objects.all().filter(notification_receiver__email=user.email))