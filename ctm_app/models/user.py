from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .customusermanager import CustomUserManager


class User(AbstractUser):
    CHOICES = (
        ("user", 'User'),
        ("admin", 'Admin')
    )
    TIER_CHOICES = (
        ("FREE", 'Free'),
        ("PRO", 'Pro'),
        ("PREMIUM", 'Premium')
    )
     
    username = None
    email = models.EmailField(_("email address"), unique=True)
    nick = models.CharField(max_length=70,blank=True) 
    ubicacion = models.CharField(max_length=255,blank=True)
    modo_oscuro=models.BooleanField(auto_created=False,default=False)
    largo_despliegue = models.IntegerField (default=20)
    name = models.CharField(max_length=255,blank=True)
    role = models.CharField(max_length=255, choices=CHOICES)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default="FREE")
    tier_inicio = models.DateField(blank=True, null=True)
    tier_fin    = models.DateField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name','last_name']

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.email}'