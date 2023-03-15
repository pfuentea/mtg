from django.db import models
from .user import User


class Contacto(models.Model):
    usuario = models.ForeignKey(User,related_name='from_contact', on_delete=models.CASCADE)
    contacto = models.ForeignKey(User,related_name='to_contact', on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
