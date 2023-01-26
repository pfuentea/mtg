from django.db import models
from .edicion import Edicion 

class Carta(models.Model):
    nombre = models.CharField(max_length=100)
    Edicion  = models.ForeignKey(Edicion, related_name='cartas', on_delete=models.CASCADE)
    number_collector =models.IntegerField()
    number_collector_txt =models.CharField(max_length=10)
    small_image=models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        card=self.nombre+"("+self.Edicion.nombre+")"
        return card
    