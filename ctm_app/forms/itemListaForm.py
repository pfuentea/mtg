from django import forms
from ..models.item_lista import ItemLista

class ItemListaForm(forms.ModelForm):
    FOIL_CHOICES = [
        (True, 'Si'),
        (False, 'No'),
    ]
    es_foil = forms.BooleanField(required=False, widget=forms.RadioSelect(choices=((True, 'Sí'), (False, 'No'))))
    class Meta:
        model=ItemLista

        fields =['cantidad','precio','observacion','es_foil']
        required=['es_foil']
        labels={
            'cantidad':('Cantidad'),
            'precio':('Precio'),
            'observacion':('Observaciones'),
            'es_foil':('Foil'), 
        }
        help_texts = {
            
        }
        error_messages = {
            'cantidad': {
                'max_length': ("No puede agregar más de 100"),
            },
            
        }
        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'observacion': forms.Textarea(attrs={'rows': 4,'class': 'form-control'})
        }