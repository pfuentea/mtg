from django.db import models
from .user import User

class Grupo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=500, blank=True)
    owner = models.ForeignKey(User, related_name='grupos_creados', on_delete=models.CASCADE)
    miembros = models.ManyToManyField(User, related_name='grupos_pertenecientes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
