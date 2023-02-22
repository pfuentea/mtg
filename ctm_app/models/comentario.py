from django.db import models

class Comentario(models.Model):
    remitente = models.TextField(max_length=100)
    email =models.TextField(max_length=500)
    mensaje =models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        cmt=self.remitente+"("+self.email+")"
        return cmt