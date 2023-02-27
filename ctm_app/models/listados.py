from django.db import models
from .user import User

class Listados(models.Model):
    B='B'
    O='O'
    SIN_DEFINIR='NA'
    DEFAULT='D'
    LIST_TYPE = (
        (B, 'Busca'),
        (O, 'Ofrece'),
        (SIN_DEFINIR, 'Sin Definir'),
        (DEFAULT, 'Default'),
        
    )
    owner = models.ForeignKey(User,related_name='listas', on_delete=models.CASCADE)
    nombre =models.TextField(max_length=100)
    tipo =  models.CharField(max_length=30, choices=LIST_TYPE,default=DEFAULT)
    descripcion =models.TextField(max_length=500,blank=True)
    referencia_web = models.TextField(max_length=500,blank=True)
    referencia_precio= models.IntegerField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expiracion = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        lista=self.nombre+":"+self.owner.name+"("+self.tipo+")"
        return lista