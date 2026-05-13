from django import forms
from ..models.listados import Listados

class ListaForm(forms.ModelForm):
    TIPO_CHOICES = [
        ('B', 'Busca'),
        ('O', 'Ofrece'),
    ]
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, widget=forms.Select)

    class Meta:
        model=Listados

        fields =['nombre','tipo','privacidad','shared_with_users','shared_with_groups','referencia_web','referencia_precio','descripcion']
        required=['nombre']
        labels={
            'nombre':('Nombre'),
            'tipo':('Tipo'),
            'privacidad':('Privacidad'),
            'shared_with_users':('Usuarios Asociados'),
            'shared_with_groups':('Grupos Asociados'),
            'referencia_web':('Referencia Web'),
            'referencia_precio':('Referencia Precio'),
            'descripcion':('Descripción'),
        }
        help_texts = {
            'nombre':'No puede quedar vacio'
        }
        error_messages = {
            'cantidad': {
                'max_length': ("No puede agregar más de 100"),
            },
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'privacidad': forms.Select(attrs={'class': 'form-select', 'id': 'id_privacidad'}),
            'shared_with_users': forms.SelectMultiple(attrs={'class': 'form-select d-none', 'id': 'id_shared_with_users'}),
            'shared_with_groups': forms.SelectMultiple(attrs={'class': 'form-select d-none', 'id': 'id_shared_with_groups'}),
            'referencia_web': forms.TextInput(attrs={'class': 'form-control'}),
            'referencia_precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 4,'class': 'form-control'})
        }