from operator import itemgetter
from django.contrib import messages
from django.shortcuts import redirect, render
import bcrypt
from .decorators import login_required
from .models import *
from datetime import datetime, timedelta



@login_required
def stats(request):
    cantidad_users=User.objects.all().count()
    cantidad_listas=Listados.objects.all().count()
    cantidad_cartas=Carta.objects.all().count()
    context={
        'cantidad_users':cantidad_users,
        'cantidad_listas':cantidad_listas,
        'cantidad_cartas':cantidad_cartas,
    }
    return render(request, 'manage/users.html', context=context )