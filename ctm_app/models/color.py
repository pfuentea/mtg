from django.db import models


class Color(models.Model):
    nombre  = models.CharField(max_length=20)
    simbolo = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)