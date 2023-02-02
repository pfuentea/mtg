from django import forms
from ..models.comentario import Comentario

class ComentarioForm(forms.ModelForm):
    class Meta:
        model=Comentario
        
        fields =['remitente','email','mensaje']
        required=['remitente','email','mensaje']
        labels={
            'remitente':('Nombre'),
            'email':('Email'),
            'mensaje':('Mensaje')
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'remitente': forms.TextInput(attrs={'class': 'form-control'}),
            'mensaje': forms.Textarea(attrs={'rows': 4,'class': 'form-control'})
        }
        help_texts = {
            
        }
        error_messages = {
            'remitente': {
                'max_length': ("Este nombre es demasiado largo"),
            },
            'mensaje': {
                'max_length': ("El comentario debe tener menos de 500 caracteres"),
            },
        }