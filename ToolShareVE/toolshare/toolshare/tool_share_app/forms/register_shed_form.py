import re

from django import forms

from tool_share_app import models


# -----------------------
# form to register a shed
# -----------------------
class ShedRegistrar(forms.ModelForm):
    class Meta:
        model = models.Address
        fields = ['street_address']
        
        widgets = { 'street_address': forms.TextInput(attrs={'class': 'form-control'}), }

    shed_name = forms.CharField(max_length=30, required=True, 
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '30 characters max'}))

    
    
    def clean_shed_name(self):
        shed_name = self.cleaned_data['shed_name']
        
        compiled_rejex = re.compile('[0-9a-zA-Z ]+')
        
        filtered_shed_name = shed_name.strip()
        
        if filtered_shed_name == '':
            raise forms.ValidationError('This field is required.')
        
        elif not compiled_rejex.match(filtered_shed_name):
            raise forms.ValidationError('Invalid shed name. Only alpha characters and numbers allowed.')
    
        return filtered_shed_name
        
   
    def clean_street_address(self):
        street_address = self.cleaned_data['street_address']
        
        compiled_rejex = re.compile('[0-9]+ [a-zA-Z\. ]+')
        
        if not compiled_rejex.match(street_address):
            raise forms.ValidationError('Invalid address. Usually addresses start with a house|place number followed by the street name.')
        
        return street_address