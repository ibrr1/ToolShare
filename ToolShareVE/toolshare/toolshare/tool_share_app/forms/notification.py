from django import forms
from tool_share_app import models


class Notification(forms.ModelForm):
    class Meta:
        model = models.Notification
        fields = []
    
    message = forms.CharField(max_length = 300, 
                              required=True, 
                              widget=forms.Textarea(attrs={'style':'resize:none;', 'maxlength': '300', 'class': 'form-control', 'rows': '5'}))
    
    def set_sender(self, sender):
        self.instance.notification_sender = sender
        
    def set_receiver(self, receiver):
        self.instance.notification_receiver = receiver
        
    def set_tool(self, tool):
        self.instance.notification_tool = tool
        
    def set_notification_type(self, not_type):
        self.instance.notification_request_type = not_type
        
    def set_notification_information(self, information):
        self.instance.notification_information = information