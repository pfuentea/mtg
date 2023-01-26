from django.db import models


class Edicion(models.Model):
    nombre = models.CharField(max_length=100)
    set_code  = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        ed=self.nombre+"("+self.set_code+")"
        return ed