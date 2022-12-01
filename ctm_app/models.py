from django.db import models
import re

from django.db.models.fields.related import create_many_to_many_intermediary_model

# Create your models here.
class UserManager(models.Manager):
    def validador_basico(self, postData):
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        SOLO_LETRAS = re.compile(r'^[a-zA-Z. ]+$')

        errors = {}

        if len(postData['name']) < 2:
            errors['firstname_len'] = "nombre debe tener al menos 2 caracteres de largo";

        if not EMAIL_REGEX.match(postData['email']):
            errors['email'] = "correo invalido"

        if not SOLO_LETRAS.match(postData['name']):
            errors['solo_letras'] = "solo letras en nombreporfavor"

        if len(postData['password']) < 4:
            errors['password'] = "contraseña debe tener al menos 8 caracteres";

        if postData['password'] != postData['password_confirm'] :
            errors['password_confirm'] = "contraseña y confirmar contraseña no son iguales. "

        
        return errors


class User(models.Model):
    CHOICES = (
        ("user", 'User'),
        ("admin", 'Admin')
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    role = models.CharField(max_length=255, choices=CHOICES)
    password = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.name}"

class Edicion(models.Model):
    nombre = models.CharField(max_length=100)
    set_code  = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        ed=self.nombre+"("+self.set_code+")"
        return ed

class Color(models.Model):
    nombre  = models.CharField(max_length=20)
    simbolo = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Tipo(models.Model):
    nombre  = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Carta(models.Model):
    nombre = models.CharField(max_length=100)
    Edicion  = models.ForeignKey(Edicion, related_name='cartas', on_delete=models.CASCADE)
    number_collector =models.IntegerField()
    small_image=models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        card=self.nombre+"("+self.Edicion.nombre+")"
        return card
    
class Listados(models.Model):
    BUSCA='Cartas que buscas'
    OFRECE='Cartas que ofrece'
    SIN_DEFINIR='Listado sin definir'
    DEFAULT='Lista por defecto'
    LIST_TYPE = (
        (BUSCA, 'Busca'),
        (OFRECE, 'Ofrece'),
        (SIN_DEFINIR, 'Sin Definir'),
        (DEFAULT, 'Default'),
        
    )
    owner = models.ForeignKey(User,related_name='listas', on_delete=models.CASCADE)
    nombre =models.TextField(max_length=100)
    tipo =  models.CharField(max_length=30, choices=LIST_TYPE,default=DEFAULT)
    descripcion =models.TextField(max_length=500)
    referencia_web = models.TextField(max_length=500)
    referencia_precio= models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ItemLista(models.Model):
    carta = models.ForeignKey(Carta, related_name='items', on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    lista=models.ForeignKey(Listados,related_name='items', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    observacion= models.TextField(max_length=500)