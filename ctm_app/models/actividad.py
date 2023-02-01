from django.db import models
from .user import User
from .listados import Listados

class Actividad(models.Model):
    actor = models.ForeignKey(User,related_name='actividades', on_delete=models.CASCADE)
    accion = models.TextField(max_length=500)
    lista = models.ForeignKey(Listados,related_name='actividades', on_delete=models.CASCADE,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    