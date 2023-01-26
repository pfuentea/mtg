from django.contrib import admin

from .models.user import User
from .models.listados import Listados
from .models.item_lista import ItemLista
from .models.carta import Carta
from .models.edicion import Edicion
from .models.color import Color
from .models.tipo import Tipo

admin.site.register(User)
admin.site.register(Edicion)
admin.site.register(Color)
admin.site.register(Tipo)
admin.site.register(Carta)
admin.site.register(Listados)
admin.site.register(ItemLista)
