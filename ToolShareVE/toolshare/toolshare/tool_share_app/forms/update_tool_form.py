from django import forms
from tool_share_app import models


class UpdateTool(forms.ModelForm):
    class Meta:
        model = models.Tool
        fields = ['name', 'description']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '30 characters maximum'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'style':'resize:none;'}),
        }

    category = forms.ModelChoiceField(queryset=models.ToolCategory.objects.all(),
                                      required=False, 
                                      widget=forms.Select(attrs={'class': 'form-control'}))

    def clean_name(self):
        name = self.cleaned_data['name']
        
        filtered_name = name.strip()
        
        if filtered_name == '':
            raise forms.ValidationError('This field is required.')
        
        if filtered_name[0].isdigit():
            raise forms.ValidationError('Invalid tool name. Only letters, number, and spaces allowed. A name starting with a number is not allowed.')
        
        for character in filtered_name:     
            if character.isdigit() or character.isspace():
                continue
                
            if not character.isalpha():
                raise forms.ValidationError('Invalid tool name.')
                    
        return filtered_name
        
        
    def clean_description(self):
        description = self.cleaned_data['description']
        
        filtered_description = description.strip()
        
        if filtered_description == '':
            raise forms.ValidationError('This field is required.')
            
        return filtered_description
    

class UpdateTool2(forms.Form):
    CONDITIONS = (
        ('', '---------'),
        ('E', 'Excellent'),
        ('G', 'Good'),
        ('R', 'Regular'),
    )

    IN_SHED_CONDITIONS = (
        ('Y', 'Shed'),
        ('N', 'Home'),
    )

    STATUS = (
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
    )

    ACTIVATE = (
        ('Activate', 'Activate'),
        ('Deactivate', 'Deactivate'),
    )

    condition = forms.ChoiceField(choices=CONDITIONS, widget=forms.Select(attrs={'class': 'form-control'}))
    in_shed = forms.ChoiceField(choices=IN_SHED_CONDITIONS, widget=forms.Select(attrs={'class': 'form-control'}), label='Tool Location?')
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UpdateTool2, self).__init__(*args, **kwargs)
   
    
    def clean_in_shed(self):
        in_shed_answer = self.cleaned_data['in_shed']
        
        flag = False
        
        if in_shed_answer == 'Y':
            shed_list = models.Shed.objects.all()
            
            for shed in shed_list:
                if shed.address.zip_code == self.user.address.zip_code:
                    flag = True
                    
            if not flag:
                raise forms.ValidationError('Shed does not exists. A shed must be registered first.')
        
        return in_shed_answer
    
    status = forms.ChoiceField(choices=STATUS, widget=forms.Select(attrs={'class': 'form-control'}))
    activate = forms.ChoiceField(choices=ACTIVATE, widget=forms.Select(attrs={'class': 'form-control'}))