from tool_share_app import models
from django import forms


class ToolAggregator(forms.ModelForm):
    class Meta:
        js = ('animations.js', 'actions.js')
        model = models.Tool
        fields = ['name']

        widgets = {
            'name': forms.TextInput(attrs={'max_length': '30', 'class': 'form-control', 'placeholder': '30 characters max'})
        }


    category = forms.ModelChoiceField(queryset=models.ToolCategory.objects.all(),
                                      widget=forms.Select(attrs={'class': 'form-control'}))


    CONDITIONS = (
        ('', '---------'),
        ('E', 'Excellent'),
        ('G', 'Good'),
        ('R', 'Regular'),
    )

    IN_SHED_CONDITIONS = (
        ('', '---------'),
        ('Y', 'Shed'),
        ('N', 'Home'),
    )

    condition = forms.ChoiceField(choices=CONDITIONS, widget=forms.Select(attrs={'class': 'form-control'}))
    in_shed = forms.ChoiceField(choices=IN_SHED_CONDITIONS, widget=forms.Select(attrs={'class': 'form-control'}), label='Tool Location?')


    description = forms.CharField(required=True,
                                   widget=forms.Textarea(attrs={'id': 'message', 'class': 'form-control', 'rows': '3', 'style':'resize:none;'}),
                                   max_length=300)
                                   

    def set_description(self, description):
        self.instance.description = description


    def clean_description(self):
        description = self.cleaned_data['description']

        filtered_description = description.strip()

        if filtered_description == '':
            raise forms.ValidationError('This field is required.')

        return filtered_description


    def set_description(self, description):
        self.instance.description = description


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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ToolAggregator, self).__init__(*args, **kwargs)


    def clean_in_shed(self):
        in_shed_answer = self.cleaned_data['in_shed']

        flag = False

        if in_shed_answer == 'Y':
            shed_list = models.Shed.objects.all()

            for shed in shed_list:
                if shed.address.zip_code == self.user.address.zip_code:
                    flag = True

            if not flag:
                raise forms.ValidationError('Shed does not exists. A shed must be registered first. Click here to register shed: ')

        return in_shed_answer
