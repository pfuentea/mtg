from operator import itemgetter
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
import bcrypt
from .decorators import login_required
from .models import *
from datetime import datetime, timedelta, date

from django.db.models.functions import TruncDate,TruncMonth
import matplotlib.pyplot as plt
from django.db.models import Count

from io import BytesIO
import base64
import calendar

@login_required
def stats(request):
    cantidad_users   = User.objects.all().count()
    cantidad_listas  = Listados.objects.all().count()
    cantidad_cartas  = Carta.objects.all().count()
    listas_busco     = Listados.objects.filter(tipo='B').count()
    listas_ofrezco   = Listados.objects.filter(tipo='O').count()
    users_free       = User.objects.filter(tier='FREE').count()
    users_pro        = User.objects.filter(tier='PRO').count()
    users_premium    = User.objects.filter(tier='PREMIUM').count()
    from .models.comentario import Comentario
    comentarios_total    = Comentario.objects.count()
    comentarios_no_leidos = Comentario.objects.filter(leido=False).count()
    context = {
        'cantidad_users':        cantidad_users,
        'cantidad_listas':       cantidad_listas,
        'cantidad_cartas':       cantidad_cartas,
        'listas_busco':          listas_busco,
        'listas_ofrezco':        listas_ofrezco,
        'users_free':            users_free,
        'users_pro':             users_pro,
        'users_premium':         users_premium,
        'comentarios_total':     comentarios_total,
        'comentarios_no_leidos': comentarios_no_leidos,
    }
    return render(request, 'manage/users.html', context=context)

@login_required
def ranking(request):
    from django.db.models import Sum

    # rank1: cartas más buscadas por versión exacta (carta + edición)
    rank1_data = (
        ItemLista.objects
        .filter(lista__tipo='B')
        .values('carta_id')
        .annotate(cantidad=Sum('cantidad'))
        .order_by('-cantidad')[:20]
    )
    qty_map_r1 = {r['carta_id']: r['cantidad'] for r in rank1_data}
    seen_r1 = set()
    rank1 = []
    for item in ItemLista.objects.filter(carta_id__in=qty_map_r1.keys(), lista__tipo='B').select_related('carta', 'carta__Edicion'):
        if item.carta_id not in seen_r1:
            seen_r1.add(item.carta_id)
            item.cantidad = qty_map_r1[item.carta_id]
            rank1.append(item)
    rank1.sort(key=lambda x: -x.cantidad)

    # rank2: cartas más buscadas por nombre (agrupando todas las ediciones)
    rank2_data = (
        ItemLista.objects
        .filter(lista__tipo='B')
        .values('carta__nombre')
        .annotate(cantidad=Sum('cantidad'))
        .order_by('-cantidad')[:20]
    )
    qty_map_r2 = {r['carta__nombre']: r['cantidad'] for r in rank2_data}
    seen_r2 = set()
    rank2 = []
    for item in ItemLista.objects.filter(carta__nombre__in=qty_map_r2.keys(), lista__tipo='B').select_related('carta', 'carta__Edicion'):
        if item.carta.nombre not in seen_r2:
            seen_r2.add(item.carta.nombre)
            item.cantidad = qty_map_r2[item.carta.nombre]
            rank2.append(item)
    rank2.sort(key=lambda x: -x.cantidad)

    context = {
        'rank1': rank1,
        'rank2': rank2,
    }
    return render(request, 'manage/ranking.html', context=context)

@login_required
def ranking_searchers(request):
    from django.http import JsonResponse
    from django.db.models import Sum

    carta_id = request.GET.get('carta_id')
    nombre   = request.GET.get('nombre')

    if carta_id:
        items = (ItemLista.objects
                 .filter(carta_id=carta_id, lista__tipo='B')
                 .select_related('lista__owner', 'carta', 'carta__Edicion'))
        titulo = None
        for it in items:
            titulo = f"{it.carta.nombre} ({it.carta.Edicion.nombre})"
            break
    elif nombre:
        items = (ItemLista.objects
                 .filter(carta__nombre=nombre, lista__tipo='B')
                 .select_related('lista__owner', 'carta', 'carta__Edicion'))
        titulo = nombre
    else:
        return JsonResponse({'titulo': '', 'searchers': []})

    searchers = {}
    for item in items:
        uid = item.lista.owner.id
        if uid not in searchers:
            searchers[uid] = {
                'id':        uid,
                'name':      item.lista.owner.name or item.lista.owner.email,
                'nick':      item.lista.owner.nick or '',
                'ubicacion': item.lista.owner.ubicacion or '',
                'cantidad':  0,
                'lista_nombre': item.lista.nombre,
                'lista_id':    item.lista.id,
            }
        searchers[uid]['cantidad'] += item.cantidad

    result = sorted(searchers.values(), key=lambda x: -x['cantidad'])
    return JsonResponse({'titulo': titulo or nombre or '', 'searchers': result})


@login_required
def user_list(request):
    import json
    usuarios = User.objects.all().order_by('-date_joined')

    # Datos por día para Chart.js
    usuarios_por_dia = (
        User.objects.annotate(fecha=TruncDate('date_joined'))
        .values('fecha').annotate(cantidad=Count('id')).order_by('fecha')
    )
    labels_dia    = [r['fecha'].strftime('%d/%m/%Y') for r in usuarios_por_dia]
    data_dia      = [r['cantidad'] for r in usuarios_por_dia]

    # Datos por mes para Chart.js
    usuarios_por_mes = (
        User.objects.annotate(fecha=TruncMonth('date_joined'))
        .values('fecha').annotate(cantidad=Count('id')).order_by('fecha')
    )
    labels_mes = [r['fecha'].strftime('%m/%Y') for r in usuarios_por_mes]
    data_mes   = [r['cantidad'] for r in usuarios_por_mes]

    hoy = date.today()
    for u in usuarios:
        u.tier_expirado = (u.tier != 'FREE' and u.tier_fin and u.tier_fin < hoy)

    context = {
        'usuarios':   usuarios,
        'hoy':        hoy,
        'labels_dia': json.dumps(labels_dia),
        'data_dia':   json.dumps(data_dia),
        'labels_mes': json.dumps(labels_mes),
        'data_mes':   json.dumps(data_mes),
    }
    return render(request, 'manage/user_list.html', context=context)


@login_required
def edit_user(request, user_id):
    admin = User.objects.get(id=request.session['user']['id'])
    if admin.role != 'admin':
        return redirect('/index')

    target = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        target.name      = request.POST.get('name', target.name).strip()
        target.email     = request.POST.get('email', target.email).strip()
        target.nick      = request.POST.get('nick', '').strip()
        target.ubicacion = request.POST.get('ubicacion', '').strip()
        target.role      = request.POST.get('role', target.role)
        target.tier      = request.POST.get('tier', target.tier)
        target.tier_inicio = request.POST.get('tier_inicio') or None
        target.tier_fin    = request.POST.get('tier_fin') or None

        nueva_pw = request.POST.get('password', '').strip()
        if nueva_pw:
            target.set_password(nueva_pw)

        try:
            target.save()
            messages.success(request, f"Usuario {target.name} actualizado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al guardar: {e}")

        return redirect('/user_list')

    context = {
        'user': admin,
        'target': target,
        'today': date.today(),
    }
    return render(request, 'manage/edit_user.html', context)

