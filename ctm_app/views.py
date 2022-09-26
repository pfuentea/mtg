from operator import itemgetter
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
        nueva_lista=Listados.objects.create(owner=user,nombre=new_list,tipo='B',referencia_web='',referencia_precio=0)
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
        nueva_lista=Listados.objects.create(owner=user,nombre=new_list,tipo='O',referencia_web='',referencia_precio=0)
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
def list_edit(request,lista_id):
    lista=Listados.objects.get(id=lista_id)
    if request.method == "POST":
        pass
    context = {
        'saludo': 'Hola',
        "lista":lista,
        "lista_id":lista_id,
        }
    return render(request, 'update_lista.html', context)

@login_required
def add_to_list(request,lista_id):
    lista=Listados.objects.get(id=lista_id)
    if request.method == "POST":
        
        set=request.POST['set']
        carta_id=request.POST['card_id']
        nombre=request.POST['nombre']
        set_name=request.POST['set_name']
        imagen=request.POST['img_small']
        img_small=imagen.split(',')

        print(img_small)
        img_small=img_small[0]
        #primero reviso si existe la edicion
        try:            
            edicion=Edicion.objects.filter(set_code=set)            
        except:
            pass

        print("Largo edicion:",len(edicion))

        if len(edicion) <1:
            print("Nueva edicion...")
            edicion=Edicion.objects.create(set_code=set, nombre=set_name)
        else:
            edicion=edicion[0]

        print("Edicion:"+edicion.nombre)
        print("carta_id:"+carta_id)
        
        print("Revisando la carta...")
        try: #intento agregar una carta nueva, si falla es que ya existe
            carta=Carta.objects.filter(number_collector=carta_id,Edicion=edicion)
            #print(carta)
            #print(len(carta))
        except:   
            pass
        if len(carta) < 1:
            #edicion=Edicion.objects.create(set_code=set, nombre=set_name)         
            print("Añadiendo Carta...")
            url_carta="https://scryfall.com/card/"+set+"/"+carta_id+"/"
           
            carta=Carta.objects.create(nombre=nombre,Edicion=edicion,number_collector=carta_id,small_image=img_small)
        else:
            carta=carta[0]
        #agregamos si es que no existe
        try:
            print("Revisando si la carta esta en la lista.")
            is_item=ItemLista.objects.filter(carta=carta,lista=lista)
            
            print(len(is_item))
        except:
            print("ERROR:consulta con problema")
        if len(is_item)<1:
            print("La Carta no existe. La agregamos...")
            messages.success(request, "Carta agregada con exito a la lista.")
            new_item=ItemLista.objects.create(carta=carta,cantidad=1,precio=0,lista=lista)
        else:
            messages.warning(request, "Carta ya existe en la lista.")
            print("La Carta ya existe.")#sumamos 1?   

            

        #print(request.POST)
        items=ItemLista.objects.filter(lista=lista)
    else:
        items=ItemLista.objects.filter(lista=lista)
    resultado=''
    context = {
                'saludo': 'Hola',
                "resultado":resultado,
                "lista_id":lista_id,
                "items":items,
                "search":"",
                "lista": lista,

            }
    return render(request, 'detalle_lista.html', context)

@login_required
def card_detail(request,item_id):
    item=ItemLista.objects.get(id=item_id)
    #print(item)
    
    context = {
                "carta":item
            }
    return render(request, 'detalle_carta.html', context)

@login_required
def card_update(request,item_id):
    item=ItemLista.objects.get(id=item_id)
    if request.method == "POST":
        cantidad=request.POST['cantidad']
        precio=request.POST['precio']
        observaciones=request.POST['observaciones']
        item.cantidad=cantidad
        item.precio=precio
        item.observaciones=observaciones
        item.save()
        messages.success(request, "Los cambios han sido guardados.")
    print(item)
    context = {
                "carta":item
            }
    return render(request, 'detalle_carta.html', context)

@login_required
def remove_from_list(request,lista_id,item_id):
    #validar que la lista es del mismo usuario

    #remover la carta de la lista
    item = ItemLista.objects.get(id=item_id)
    item.delete()
    return redirect('/list/'+str(lista_id))
    