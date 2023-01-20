from operator import itemgetter
from django.contrib import messages
from django.shortcuts import redirect, render
import bcrypt
from .decorators import login_required
from .models import *
from datetime import datetime, timedelta,timezone
from django.http import HttpRequest
import pytz

@login_required
def index(request):

    user= User.objects.get(id=request.session['user']['id'])
    listas_hunt= Listados.objects.filter(owner=user,tipo='B')
    listas_off= Listados.objects.filter(owner=user,tipo='O')
    context = {
            'saludo': 'Hola',
            "listas_hunt":listas_hunt, 
            "listas_off":listas_off
        }
    print (f"USer:{request.session['user']}")
    return render(request, 'index.html', context=context )

@login_required
def list_hunt(request):
    user_id=request.session['user']['id']
        #print (f"User_id:{user_id}")
    user= User.objects.get(id=user_id)
    
    if request.method == "GET":
        
        listas= Listados.objects.filter(owner=user,tipo='B')
        result=[]
        for l in listas:
            estado="Activa"
            ahora = datetime.now(timezone.utc) #datetime.datetime
            ultima_act=l.updated_at
            diff=ahora - ultima_act       
            dias=divmod(diff.total_seconds() ,24 * 60 * 60 )[0] 
            if dias >14:
                estado="Expirada"

            new_elem={
                            'owner':l.owner ,
                            'nombre':l.nombre,
                            'id':l.id,
                            'items':l.items,
                            'estado':estado
                        }
            result.append(new_elem)       

        context = {
            'saludo': 'Hola',
            "listas":result
        }
        return render(request, 'hunt.html', context)
    if request.method == "POST":
        new_list=request.POST['new_list']
        nueva_lista=Listados.objects.create(owner=user,nombre=new_list,tipo='B',referencia_web='',referencia_precio=0)
        return redirect('/list/hunt')

@login_required
def activar(request,lista_id):
    lista=Listados.objects.get(id=lista_id)
    ahora = datetime.now(timezone.utc) #datetime.datetime
    lista.updated_at=ahora
    lista.save()

    previous_url = request.META.get('HTTP_REFERER')
    print(previous_url)

    return redirect(previous_url)
    

@login_required
def desactivar(request,lista_id):
    lista=Listados.objects.get(id=lista_id)
    ahora = datetime.now(timezone.utc) #datetime.datetime
    lista.updated_at=ahora- timedelta(days=14) #no funciona porque al actualizar con -14 días se actualiza con la fecha actual
    lista.save()
    if lista.tipo == 'B':
        return redirect('/list/hunt')
    return redirect('/list/offer')

@login_required
def list_offer(request):
    user_id=request.session['user']['id']
        #print (f"User_id:{user_id}")
    user= User.objects.get(id=user_id)
    if request.method == "GET":
        
        listas= Listados.objects.filter(owner=user,tipo='O')
        result=[]
        for l in listas:
            estado="Activa"
            ahora = datetime.now(timezone.utc) #datetime.datetime
            ultima_act=l.updated_at
            diff=ahora - ultima_act       
            dias=divmod(diff.total_seconds() ,24 * 60 * 60 )[0] 
            if dias >14:
                estado="Expirada"

            new_elem={
                            'owner':l.owner ,
                            'nombre':l.nombre,
                            'id':l.id,
                            'items':l.items,
                            'estado':estado
                        }
            result.append(new_elem)  
        context = {
            'saludo': 'Hola',
            "listas":result
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
    ahora = datetime.now(timezone.utc) #datetime.datetime
    ultima_act=lista.updated_at.replace(tzinfo=pytz.UTC)
    diff=ahora - ultima_act
    #minutos=divmod(diff.total_seconds() ,  60 )[0]
    #horas=divmod(diff.total_seconds() , 60 * 60 )[0]
    dias=divmod(diff.total_seconds() ,24 * 60 * 60 )[0]
    #print(ultima_act)
    
    if request.method == "GET":        
        
        items= ItemLista.objects.filter(lista=lista)
        lstdict=[]
        for elemento in items:
            
            #print(f"carta_id:{elemento.carta.id}/{elemento.carta.nombre}")

            resultado1=ItemLista.objects.filter(carta=elemento.carta).exclude(lista__owner=elemento.lista.owner)
            if len(resultado1) >0:
                #print("Encontre la carta en otra lista!")
                for r in resultado1:
                    #print(f"lista:{r.lista.nombre},dueño:{r.lista.owner.name}")
                    #busco el indice donde exista un dict con name= r.lista.owner.name y lname=r.lista.nombre, si no existe: creo el dict y lo agrego
                    indice=next((i for i, x in enumerate(lstdict) if x["name"] == r.lista.owner.name and  x["lname"] ==r.lista.nombre), None)
                    if indice is None:
                        new_elem={
                            'name':r.lista.owner.name ,
                            'lname':r.lista.nombre,
                            'list_id':r.lista.id,
                            'owner_id':r.lista.owner.id,
                            'qty':1
                        }
                        lstdict.append(new_elem)
                    else:
                        lstdict[indice]['qty']+=1

        #print(lstdict)
        context = {
            'saludo': 'Hola',
            "items":items,
            "lista_id":lista_id,
            "lista":lista,
            "duracion":14-dias,
            "resultado":lstdict
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
                "search":"",
                "duracion":duracion
            }
        return render(request, 'detalle_lista.html', context)
        new_carta=request.POST['new_card']

        nueva_lista=Listados.objects.create(owner=user,nombre=new_list,tipo='O')
        return redirect('/list/offer')

def share(request,lista_id):
    lista=Listados.objects.get(id=lista_id)
    items= ItemLista.objects.filter(lista=lista)
    usuario=lista.owner.name
    vista="lista"
    if 'view' in request.GET:
        if request.GET['view'] == 'img' :
            vista="imgs"

    context = {
            'saludo': 'Hola',
            "items":items,
            "lista_id":lista_id,
            "lista":lista,
            "usuario":usuario,
            "vista":vista
        }
    return render(request, 'share.html', context)

def share_all(request,lista_id):
    lista=Listados.objects.get(id=lista_id)
    items= ItemLista.objects.filter(lista=lista)
    usuario=lista.owner.name
    vista="lista"
    if 'view' in request.GET:
        if request.GET['view'] == 'img' :
            vista="imgs"

    context = {
            'saludo': 'Hola',
            "items":items,
            "lista_id":lista_id,
            "lista":lista,
            "usuario":usuario,
            "vista":vista
        }
    return render(request, 'share.html', context)

@login_required
def list_edit(request,list_id):
    lista=Listados.objects.get(id=list_id)
    usuario=lista.owner.name
        
    if request.method == "POST":
        lista.nombre=request.POST['nombre']
        lista.tipo=request.POST['tipo']
        lista.referencia_precio=request.POST['ref_precio']
        lista.referencia_web=request.POST['ref_web']
        lista.descripcion=request.POST['descripcion']
        lista.save()
        messages.success(request, "Lista modificada con exito.")

    context = {
        'saludo': 'Hola',
        "lista":lista,
        "lista_id":list_id,
        "usuario":usuario,
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

        #print("Largo edicion:",len(edicion))

        if len(edicion) <1:
            print("Nueva edicion...")
            edicion=Edicion.objects.create(set_code=set, nombre=set_name)
        else:
            edicion=edicion[0]

        print("Edicion:"+edicion.nombre)
        print("carta_id:"+carta_id)
        last_char = carta_id[-1]
        print(f"ultimo char:{last_char}")
        try:
            x=int(last_char)
            carta_id_num=carta_id
            
        except:
            carta_id_num=carta_id[:-1]

        print("Revisando la carta...")
        try: #intento agregar una carta nueva, si falla es que ya existe
            carta=Carta.objects.filter(number_collector_txt=carta_id,Edicion=edicion)
            #print(carta)
            #print(len(carta))
        except:   
            pass

        if len(carta) < 1:
            #edicion=Edicion.objects.create(set_code=set, nombre=set_name)         
            print("Añadiendo Carta...")
            url_carta="https://scryfall.com/card/"+set+"/"+carta_id+"/"
           
            carta=Carta.objects.create(nombre=nombre,Edicion=edicion,number_collector_txt=carta_id,small_image=img_small,number_collector=carta_id_num)
        else:
            carta=carta[0]
        #agregamos si es que no existe
        try:
            print("Revisando si la carta esta en la lista.")
            is_item=ItemLista.objects.filter(carta=carta,lista=lista)
            
            print(f"# veces en la lista: {len(is_item)}")
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
        observacion=request.POST['observacion']
        item.cantidad=cantidad
        item.precio=precio
        item.observacion=observacion
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
    

@login_required
def delete_list(request,lista_id):
    lista=Listados.objects.get(id=lista_id)
    lista.delete()
    return redirect('/list/hunt')

@login_required
def view_all_hunt(request):
    user_id=request.session['user']['id']
        #print (f"User_id:{user_id}")
    user= User.objects.get(id=user_id)
    
    items= ItemLista.objects.filter(lista__owner=user,lista__tipo='B')
    context = {
                
                "items":items,
                "search":"",
                "tipo":'B'
            }
    return render(request, 'detalle_lista_all.html', context)