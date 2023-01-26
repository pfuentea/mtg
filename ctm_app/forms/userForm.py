from django import forms
from ..models.user import User

class UserForm(forms.ModelForm):
    class Meta:
        model=User
        
        fields =['name','email','nick','ubicacion']
        required=['name','email']
        labels={
            'name':('Nombre'),
            'nick':('Username'),
        }
        help_texts = {
            
        }
        error_messages = {
            'name': {
                'max_length': ("Este nombre es demasiado largo"),
            },
        }