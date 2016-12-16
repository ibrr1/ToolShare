from django import forms

#--------------------------------------------------------------------------------------------------
# global function used to validate names when no special symbols and numbers are allowed to be used
#--------------------------------------------------------------------------------------------------
def validate_name(name, type_name):
    for character in name:
        if not character.isalpha() or character.isdigit():
            raise forms.ValidationError('Invalid ' + type_name + ' Name. Only alpha characters allowed.')

    return name


# end validate_name