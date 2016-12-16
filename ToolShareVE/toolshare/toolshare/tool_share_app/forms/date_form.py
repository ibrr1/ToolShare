from django import forms
from tool_share_app import models
import datetime
from django.forms.extras.widgets import SelectDateWidget


class RequestDate(forms.Form):
	start_date = forms.DateField(widget=SelectDateWidget, initial=datetime.date.today)

	def clean_start_date(self):
	 	return self.cleaned_data['start_date']

	
class ReturnDate(forms.Form):
	return_date = forms.DateField(widget=SelectDateWidget, initial=datetime.date.today)	
	
	def clean_return_date(self):
	 	return self.cleaned_data['return_date']