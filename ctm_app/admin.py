from django.contrib import admin
from .models import User, Edicion,Color,Tipo,Carta,Listados,ItemLista

# Register your models here.

admin.site.register(User)
admin.site.register(Edicion)
admin.site.register(Color)
admin.site.register(Tipo)
admin.site.register(Carta)
admin.site.register(Listados)
admin.site.register(ItemLista)
