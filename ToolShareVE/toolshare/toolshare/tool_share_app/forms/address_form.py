import re

from django import forms

from tool_share_app import models


# -----------------------------------------------
# form dedicated to the registration of addresses 
# -----------------------------------------------
class AddressRegistrar(forms.ModelForm):
    class Meta:
        model = models.Address
        fields = ['street_address', 'city', 'zip_code']
        
        widgets = {
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '50 characters maximum'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
        }

    state = forms.ModelChoiceField(queryset=models.States.objects.all(), 
                                   widget=forms.Select(attrs={'class': 'form-control'}))

    # validates street address                             
    def clean_street_address(self):
        street_address = self.cleaned_data['street_address']
        
        compiled_rejex = re.compile('[0-9]+ [a-zA-Z\. ]+')
        
        if not compiled_rejex.match(street_address):
            raise forms.ValidationError('Invalid address. Usually addresses start with a house|place number followed by the street name.')
        
        return street_address
        
        
    # validates the city name    
    def clean_city(self):
        city = self.cleaned_data['city']
        
        compiled_rejex = re.compile('[a-zA-Z ]+')
        
        if not compiled_rejex.match(city):
            raise forms.ValidationError('Invalid city name.')

        filtered_city = city.strip()

        if filtered_city == '':
            raise forms.ValidationError('This field is required.')
            
        return city
        

    # sets the state to the current form instance
    def set_state(self, state):
        self.instance.state = state
        
        
    # validates the zip code introduced
    def clean_zip_code(self):
        zip_code = self.cleaned_data['zip_code']

        if len(zip_code) < 5:
            raise forms.ValidationError('Zip code must be composed by 5 characters.')

        for number in zip_code:
            if not number.isdigit():
                raise forms.ValidationError('Only numbers allowed in the zip code.')

        return zip_code

# end AddressRegistrar