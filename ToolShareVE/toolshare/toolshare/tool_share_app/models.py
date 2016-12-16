from django.db import models
import datetime


class States(models.Model):
    state_name = models.CharField(max_length=100)

    def __str__(self):
        return self.state_name


class Address(models.Model):
    zip_code = models.CharField(max_length=5)
    state = models.ForeignKey(States)
    city = models.CharField(max_length=50)
    street_address = models.CharField(max_length=100, help_text='Ex.: 2350 Broad hollow Road | Rd.')

    def __str__(self):
        return self.street_address + ', ' + self.city + ', ' + self.zip_code


class User(models.Model):
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    email = models.EmailField()
    password = models.CharField(max_length=50)
    admin = models.BooleanField(default=False)
    address = models.OneToOneField(Address)

    def __str__(self):
        return self.email


class Shed(models.Model):
    name = models.CharField(max_length=30)
    address = models.OneToOneField(Address)

    def __str__(self):
        return self.name


class ToolCategory(models.Model):
    category = models.CharField(max_length=50)

    def __str__(self):
        return self.category


class Tool(models.Model):
    name = models.CharField(max_length=30)
    condition = models.CharField(max_length=30)
    status = models.CharField(max_length=30)
    activate = models.CharField(max_length=30)
    description = models.CharField(max_length=300)
    location = models.ForeignKey(Address)
    category = models.ForeignKey(ToolCategory)
    owner = models.ForeignKey(User)

    def __str__(self):
        return str(self.id) + '. ' + self.name


class ToolBorrowingRequest(models.Model):
    requester = models.ForeignKey(User)
    date_request = models.DateField()
    date_return = models.DateField()
    tool_requested = models.ForeignKey(Tool)

    def __str__(self):
        return "requester: " + self.requester.email + " - tool requested: " + self.tool_requested.name


class Notification(models.Model):
    notification_request_type = models.CharField(max_length=1)
    notification_receiver = models.ForeignKey(User)
    notification_sender = models.CharField(max_length=100, default='')
    notification_information = models.CharField(max_length=256)
    notification_tool = models.ForeignKey(Tool, blank=True, null=True)
    notification_timestamp = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        if not self.notification_tool:
            return 'NA'
            
        return 'sender: ' + self.notification_tool.owner.first_name + ' - receiver: ' + self.notification_receiver.first_name


class CurrentlyBorrowedTools(models.Model):
    possesor = models.ForeignKey(User)
    tool = models.OneToOneField(Tool)
    start_time = models.DateField()
    return_time = models.DateField()
    flag = models.BooleanField(default=False)

    def __str__(self):
        return 'Possesor: ' + self.possesor.first_name + ' ' + self.possesor.last_name + ' ' + self.tool.name


class DataStatistics(models.Model):
    requester = models.ForeignKey(User)
    tool_requested = models.ForeignKey(Tool)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return "requester: " + self.requester.email + " - tool requested: " + self.tool_requested.name
