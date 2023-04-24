from operator import itemgetter
from django.contrib import messages
from django.shortcuts import redirect, render
import bcrypt
from .decorators import login_required
from .models import *
from datetime import datetime, timedelta

from django.db.models.functions import TruncDate,TruncMonth
import matplotlib.pyplot as plt
from django.db.models import Count

from io import BytesIO
import base64
import calendar

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

@login_required
def ranking(request):
    context={
       
    }
    return render(request, 'manage/ranking.html', context=context )

@login_required
def user_list(request):
    usuarios=User.objects.all().order_by('-created_at')

    #usuarios por día
    usuarios_por_dia = User.objects.annotate(fecha=TruncDate('created_at')).values('fecha').annotate(cantidad=Count('id'))
    fechas = []
    cantidades = []
    for registro in usuarios_por_dia: 
        #print(registro['fecha'])
        fechas.append(registro['fecha'])
        cantidades.append(registro['cantidad'])


    plt.bar(fechas, cantidades)
    plt.xticks(fechas, [fecha.strftime('%Y-%m-%d') for fecha in fechas], rotation=45)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64_dia = base64.b64encode(buf.getvalue()).decode('utf-8')


    #usuarios por mes
    usuarios_por_mes = User.objects.annotate(fecha=TruncMonth('created_at')).values('fecha').annotate(cantidad=Count('id'))
    meses = []
    cantidades2 = []
    for registro2 in usuarios_por_mes:
        mes = registro2['fecha'].strftime('%Y-%m')
        meses.append(mes)
        cantidades2.append(registro2['cantidad'])

    fig2 = plt.figure()

    plt.bar(meses, cantidades2)
    nombres_meses = [datetime.strptime(m, '%Y-%m').strftime('%m/%y') for m in meses]
    plt.xticks(meses, nombres_meses, rotation=45)

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64_mes = base64.b64encode(buf.getvalue()).decode('utf-8')


    context={
        'image_base64_dia': image_base64_dia,
        'image_base64_mes': image_base64_mes,
        'usuarios':usuarios,
        
    }
    return render(request, 'manage/user_list.html', context=context )

