from django.contrib import messages
from django.shortcuts import redirect, render
import bcrypt
from .decorators import login_required
from .models import *


@login_required
def index(request):

    context = {
        'saludo': 'Hola'
    }
    return render(request, 'index.html', context)

@login_required
def list_hunt(request):
    user_id=request.session['user']['id']
        #print (f"User_id:{user_id}")
    user= User.objects.get(id=user_id)
    if request.method == "GET":
        
        listas= Listados.objects.filter(owner=user,tipo='B')
        context = {
            'saludo': 'Hola',
            "listas":listas
        }
        return render(request, 'hunt.html', context)
    if request.method == "POST":
        new_list=request.POST['new_list']
        nueva_lista=Listados.objects.create(owner=user,nombre=new_list,tipo='B')
        return redirect('/list/hunt')


@login_required
def list_offer(request):
    user_id=request.session['user']['id']
        #print (f"User_id:{user_id}")
    user= User.objects.get(id=user_id)
    if request.method == "GET":
        
        listas= Listados.objects.filter(owner=user,tipo='O')
        context = {
            'saludo': 'Hola',
            "listas":listas
        }
        return render(request, 'offer.html', context)
    if request.method == "POST":
        new_list=request.POST['new_list']
        nueva_lista=Listados.objects.create(owner=user,nombre=new_list,tipo='O')
        return redirect('/list/offer')

@login_required
def list_detail(request,lista_id):
    user_id=request.session['user']['id']
    #print (f"User_id:{user_id}")
    user= User.objects.get(id=user_id)
    lista=Listados.objects.get(id=lista_id)
    if request.method == "GET":        
        items= ItemLista.objects.filter(lista=lista)
        context = {
            'saludo': 'Hola',
            "items":items,
            "lista_id":lista_id,
            "lista":lista
        }
        return render(request, 'detalle_lista.html', context)
    if request.method == "POST":
        if request.POST['action'] == 'search':
            resultado=Carta.objects.filter(nombre=request.POST['searching_card'])
            items= ItemLista.objects.filter(lista=lista)
            context = {
                'saludo': 'Hola',
                "resultado":resultado,
                "lista_id":lista_id,
                "items":items,
                "search":""

            }
        return render(request, 'detalle_lista.html', context)
        new_carta=request.POST['new_card']

        nueva_lista=Listados.objects.create(owner=user,nombre=new_list,tipo='O')
        return redirect('/list/offer')

@login_required
def add_to_list(request,lista_id):
    if request.method == "POST":
        set=request.POST['set']
        id=request.POST['id']
        nombre=request.POST['nombre']

        print(request.POST)
    context = {
                'saludo': 'Hola',
                "resultado":resultado,
                "lista_id":lista_id,
                "items":items,
                "search":""

            }
    return render(request, 'detalle_lista.html', context)

