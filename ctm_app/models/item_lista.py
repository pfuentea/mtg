from django.db import models

from .carta import Carta
from .listados import Listados

class ItemLista(models.Model):
    carta = models.ForeignKey(Carta, related_name='items', on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    lista=models.ForeignKey(Listados,related_name='items', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    observacion= models.TextField(max_length=500)
    def __str__(self):
        item=self.carta.nombre+"("+self.carta.Edicion.nombre+"):"+self.lista.nombre+"("+str(self.cantidad)+")"
        return item