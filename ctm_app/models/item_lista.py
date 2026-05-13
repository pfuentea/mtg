from django.db import models

from .carta import Carta
from .listados import Listados

class ItemLista(models.Model):
    LANG_CHOICES = (
        ('EN', 'English'),
        ('ES', 'Spanish'),
        ('JP', 'Japanese'),
        ('IT', 'Italian'),
        ('PT', 'Portuguese'),
        ('FR', 'French'),
        ('DE', 'German'),
        ('RU', 'Russian'),
        ('KO', 'Korean'),
        ('ZH', 'Chinese'),
    )
    COND_CHOICES = (
        ('NM', 'Near Mint'),
        ('LP', 'Lightly Played'),
        ('MP', 'Moderately Played'),
        ('HP', 'Heavily Played'),
        ('DMG', 'Damaged'),
    )
    carta = models.ForeignKey(Carta, related_name='items', on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1,blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2,blank=True)
    lista=models.ForeignKey(Listados,related_name='items', on_delete=models.CASCADE)
    idioma = models.CharField(max_length=2, choices=LANG_CHOICES, default='EN')
    estado_fisico = models.CharField(max_length=3, choices=COND_CHOICES, default='NM')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    observacion= models.TextField(max_length=500,blank=True)
    es_foil=models.BooleanField(auto_created=False,blank=True, default=False)
    es_etched=models.BooleanField(auto_created=False,blank=True, default=False)
    esta_firmada=models.BooleanField(auto_created=False,blank=True, default=False)
    def __str__(self):
        item=self.carta.nombre+"("+self.carta.Edicion.nombre+"):"+self.lista.nombre+"(qty:"+str(self.cantidad)+")"
        return item