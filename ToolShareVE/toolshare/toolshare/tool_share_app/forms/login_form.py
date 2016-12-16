from django import forms

# form found in the login page
class UserLogger(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password'}))


# end UserLogger