from decimal import Decimal
from django import forms
from ..models.item_lista import ItemLista

class ItemListaForm(forms.ModelForm):
    FOIL_CHOICES = [
        (True, 'Si'),
        (False, 'No'),
    ]
    es_foil = forms.BooleanField(required=False, widget=forms.RadioSelect(choices=((True, 'Sí'), (False, 'No'))))

    def clean_precio(self):
        value = self.cleaned_data.get('precio')
        if value is None or value == '':
            return Decimal('0')
        if value < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return value

    def clean_cantidad(self):
        value = self.cleaned_data.get('cantidad')
        if value is None or value == '':
            return 1
        if value < 1:
            raise forms.ValidationError("La cantidad debe ser al menos 1.")
        return value

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