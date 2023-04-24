from django import forms
from ..models.user import User

class UserForm(forms.ModelForm):
    MODO_OSCURO_CHOICES = [
        (True, 'Sí'),
        (False, 'No'),
    ]
    modo_oscuro = forms.ChoiceField(choices=MODO_OSCURO_CHOICES, widget=forms.RadioSelect, label="Modo Oscuro")

    OPCIONES_LARGO_DESPLIEGUE = (
        (5, '5'),
        (10, '10'),
        (20, '20'),
        (40, '40'),
        (-1, '-1'),
    )
    largo_despliegue = forms.ChoiceField(choices=OPCIONES_LARGO_DESPLIEGUE,label="Cantidad de Resultados")

    class Meta:
        model=User
        
        fields =['name','email','nick','ubicacion','modo_oscuro','largo_despliegue']
        required=['name','email']
        labels={
            'name':('Nombre'),
            'nick':('Username'),
            'modo_oscuro':('Modo Oscuro'),
            'largo_despliegue':('Mostrar n Registros'),
        }
        help_texts = {
            
        }
        error_messages = {
            'name': {
                'max_length': ("Este nombre es demasiado largo"),
            },
        }
        