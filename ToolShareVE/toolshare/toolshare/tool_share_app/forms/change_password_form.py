from django import forms
from tool_share_app import models


class ChangePassword(forms.Form):      
    first_password = ''
    password_error = False
    
    current_password = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password'}))
    new_password = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password', 'placeholder': '6 characters minimum'}))
    new_password_verification = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password'}))
  
    def clean_new_password(self):
        password = self.cleaned_data['new_password']

        if len(password) < 6:
            ChangePassword.password_error = True
            raise forms.ValidationError('Password field must contain at least 6 characters.')

        ChangePassword.first_password = password

        return password
        
        
    def clean_new_password_verification(self):
        password = self.cleaned_data['new_password_verification']

        if password != ChangePassword.first_password:
            if ChangePassword.password_error == False:
                raise forms.ValidationError('Password field and password verification field must contain the same value.')
            else:
                ChangePassword.password_error = False

        return password


    def clean_current_password(self):
        return self.cleaned_data['current_password']

# end AddressRegistrar