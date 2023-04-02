from operator import itemgetter
from django.contrib import messages
from django.shortcuts import redirect, render
import bcrypt
from .decorators import login_required
from .models import *
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from django.db.models import Count


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

    registrations_by_day = User.objects \
        .annotate(day=Count('created_at', distinct=True)) \
        .values_list('day', flat=True)
    registrations_by_month = User.objects \
        .annotate(month=Count('created_at', distinct=True)) \
        .values_list('month', flat=True)
    print(registrations_by_day)
    # Generar los gráficos
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
    ax[0].plot(registrations_by_day)
    ax[0].set_ylabel('N° de usuarios registrados')
    ax[0].set_xlabel('Days since the first registration')
    ax[0].set_title('Usuarios registrados por dia')
    ax[0].grid(True)
    ax[1].plot(registrations_by_month)
    ax[1].set_ylabel('N° de usuarios registrados')
    ax[1].set_xlabel('Months since the first registration')
    ax[1].set_title('Usuarios registrados por mes')
    ax[1].grid(True)

    # Guardar el gráfico como un archivo PNG
    plt.savefig('./ctm_app/static/user_registrations.png')

    context={
        'usuarios':usuarios,
        'registrations_by_day': registrations_by_day,
        'registrations_by_month': registrations_by_month,
        'total_users': User.objects.count(),
    }
    return render(request, 'manage/user_list.html', context=context )

