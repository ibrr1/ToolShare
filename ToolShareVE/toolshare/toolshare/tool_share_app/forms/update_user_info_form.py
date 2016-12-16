from django import forms
from tool_share_app.forms.validate_name_function import validate_name

# Manage Account
class ManageAccount(forms.Form):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '30', 'placeholder': '30 characters maximum'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '30', 'placeholder': '30 characters maximum'}))

    first_password = ''  # helps as a holder to test the password comparison
    password_error = False

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']

        return validate_name(first_name, 'First')

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']

        return validate_name(last_name, 'Last')