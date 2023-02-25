from django import forms
from ..models.user import User

class UserForm(forms.ModelForm):
    MODO_OSCURO_CHOICES = [
        (True, 'Sí'),
        (False, 'No'),
    ]
    modo_oscuro = forms.ChoiceField(choices=MODO_OSCURO_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model=User
        
        fields =['name','email','nick','ubicacion','modo_oscuro']
        required=['name','email']
        labels={
            'name':('Nombre'),
            'nick':('Username'),
            'modo_oscuro':('Modo Oscuro'),
        }
        help_texts = {
            
        }
        error_messages = {
            'name': {
                'max_length': ("Este nombre es demasiado largo"),
            },
        }
        