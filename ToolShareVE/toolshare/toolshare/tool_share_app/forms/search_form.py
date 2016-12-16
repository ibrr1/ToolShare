__author__ = 'ibrahim'
from tool_share_app import models


from django import forms


# form found in the login page
class SearchForm(forms.Form):
    text = forms.CharField(label = 'Tool name (Optional)' , 
                           required=False, 
                           widget=forms.TextInput(attrs={'class': 'form-control', 
                                                         'placeholder': '30 characters max', 
                                                         'id': 'tool_name_search'}))
   
    category = forms.ModelChoiceField(label='Category (Optional)', 
                                      required=False, 
                                      queryset=models.ToolCategory.objects.all(), 
                                      widget=forms.Select(attrs={'class': 'form-control'}))

    CONDITIONS = (
        ('', '---------'),
        ('Excellent', 'Excellent'),
        ('Good', 'Good'),
        ('Regular', 'Regular'),
    )

    TOOL_LOCATION = (
        ('', '---------'),
        ('shed', 'Shed'),
        ('home', 'Home'),
    )

    condition = forms.ChoiceField(label='Condition (Optional)', 
                                  required=False, 
                                  choices=CONDITIONS, 
                                  widget=forms.Select(attrs={'class': 'form-control'}))
                                  
    tool_location = forms.ChoiceField(label='Tool Location (Optional)', 
                                      required=False, 
                                      choices=TOOL_LOCATION, 
                                      widget=forms.Select(attrs={'class': 'form-control'}))

