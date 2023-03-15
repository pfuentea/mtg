from django.db import models
from .user import User


class Mensaje(models.Model):
    from_user = models.ForeignKey(User,related_name='enviados', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User,related_name='recibidos', on_delete=models.CASCADE)
    contenido =models.TextField(max_length=500)
    estado=models.TextField(max_length=500,default='enviado')
    respuesta_a = models.ForeignKey('self', null=True, blank=True, related_name='respuestas', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
