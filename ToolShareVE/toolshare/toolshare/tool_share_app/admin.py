from django.contrib import admin
from . import models

admin.site.register(models.User)
admin.site.register(models.Notification)
admin.site.register(models.Address)
admin.site.register(models.Shed)
admin.site.register(models.Tool)
admin.site.register(models.ToolCategory)
admin.site.register(models.ToolBorrowingRequest)
admin.site.register(models.States)
admin.site.register(models.CurrentlyBorrowedTools)
admin.site.register(models.DataStatistics)