from django import forms
from tool_share_app.forms.validate_name_function import validate_name


class UserRegistrar(forms.Form):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 
                                               'maxlength': '30', 'placeholder': '30 characters maximum',}))
                                               
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 
                                                'maxlength': '30', 'placeholder': '30 characters maximum'}))
                                                
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 
                                                'maxlength': '30', 'placeholder': '30 characters maximum'}), 
                                                help_text='Ex.: example@domain.com')
    
    password = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password', 'placeholder': '6 characters minimum'}))
    password_verification = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password'}))

    first_password = ''
    password_error = False
    
    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']

        return validate_name(first_name, 'First')


    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']

        return validate_name(last_name, 'Last')


    def clean_password(self):
        password = self.cleaned_data['password']

        if len(password) < 6:
            UserRegistrar.password_error = True
            raise forms.ValidationError('Password field must contain at least 6 characters.')

        UserRegistrar.first_password = password

        return password


    def clean_password_verification(self):
        password = self.cleaned_data['password_verification']

        if password != UserRegistrar.first_password:
            if UserRegistrar.password_error == False:
                raise forms.ValidationError('Password field and password verification field must contain the same value.')
            else:
                UserRegistrar.password_error = False

        return password
