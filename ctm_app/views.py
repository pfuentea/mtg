from operator import itemgetter
from django.contrib import messages
from django.shortcuts import redirect, render
import bcrypt
from .decorators import login_required
#importacion de clases
from .models.user import User
from .models.listados import Listados
from .models.item_lista import ItemLista
from .models.carta import Carta
from .models.edicion import Edicion
from .models.actividad import Actividad

from .models.comentario import Comentario
from .forms.comentarioForm import ComentarioForm
from .forms.itemListaForm import ItemListaForm

from datetime import datetime, timedelta,timezone
from django.http import HttpRequest
import pytz

def landing(request):
    context = {
               
            }
    return render(request, 'landing.html', context=context )

@login_required
def index(request):

    user= User.objects.get(id=request.session['user']['id'])
    listas_hunt= Listados.objects.filter(owner=user,tipo='B')
    listas_off= Listados.objects.filter(owner=user,tipo='O')
    last_act=Actividad.objects.all().order_by('-updated_at')[:10]
    context = {
            'saludo': 'Hola',
            "listas_hunt":listas_hunt, 
            "listas_off":listas_off,
            "actividades":last_act,
            "user":user
        }
    #print (f"USer:{request.session['user']}")
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
            fecha_exp=l.expiracion.replace(tzinfo=pytz.UTC)
            diff= fecha_exp - ahora        
            dias=divmod(diff.total_seconds() ,24 * 60 * 60 )[0] 
            if dias < 0:
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
            "listas":result,
            "user":user
        }
        return render(request, 'hunt.html', context)
    if request.method == "POST": #creacion de nueva lista
        new_list=request.POST['new_list']
        dos_semanas= datetime.now(timezone.utc) + timedelta(days=14)
        nueva_lista=Listados.objects.create(owner=user,nombre=new_list,tipo='B',referencia_web='',referencia_precio=0,expiracion=dos_semanas)
        # esta accion registra una actividad

        mensaje=f" ha creado la lista de busqueda"
        new_act=Actividad.objects.create(actor=user,accion=mensaje,lista=nueva_lista)  

        return redirect('/list/hunt')

@login_required
def activar(request,lista_id):
    lista=Listados.objects.get(id=lista_id)
    dos_semanas = datetime.now(timezone.utc) + timedelta(days=14)#datetime.datetime
    lista.expiracion=dos_semanas
    lista.save()
    messages.success(request, "La lista ha sido activada con éxito!")
    previous_url = request.META.get('HTTP_REFERER')
    print(previous_url)

    return redirect(previous_url)
    

@login_required
def desactivar(request,lista_id):
    lista=Listados.objects.get(id=lista_id)
    ahora = datetime.now(timezone.utc) #datetime.datetime
    lista.expiracion=ahora
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
            fecha_exp=l.expiracion.replace(tzinfo=pytz.UTC)
            diff= fecha_exp - ahora        
            dias=divmod(diff.total_seconds() ,24 * 60 * 60 )[0] 
            if dias < 0:
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
            "listas":result,
            "user":user
        }
        return render(request, 'offer.html', context)
    if request.method == "POST":
        new_list=request.POST['new_list']
        nueva_lista=Listados.objects.create(owner=user,nombre=new_list,tipo='O',referencia_web='',referencia_precio=0)
        # esta accion registra una actividad
        mensaje=f" ha creado la lista para ofrecer"
        new_act=Actividad.objects.create(actor=user,accion=mensaje,lista=nueva_lista)       

        return redirect('/list/offer')

@login_required
def list_detail(request,lista_id):
    user_id=request.session['user']['id']
    #print (f"User_id:{user_id}")
    user= User.objects.get(id=user_id)
    lista=Listados.objects.get(id=lista_id)
    ahora = datetime.now(timezone.utc) #datetime.datetime
    fecha_exp=lista.expiracion.replace(tzinfo=pytz.UTC)
    diff= fecha_exp - ahora     

    dias=divmod(diff.total_seconds() ,24 * 60 * 60 )[0]

    #revisar que la lista sea del mismo usuario

    if user != lista.owner:
        print("Esta tratando de ver una lista que no es de el")
        messages.warning(request, "Intentas ver una lista de la que no eres propietario!")
        return redirect("/index")
    else:
        print("todo ok!")
    #print(f"dias:{dias}") 
    #minutos=divmod(diff.total_seconds() ,  60 )[0]
    #horas=divmod(diff.total_seconds() , 60 * 60 )[0]
  
    #print(ultima_act)
    
    if request.method == "GET":        
        #aca hacemos la busqueda en otras listas
        #obtenemos las cartas de la lista
        items= ItemLista.objects.filter(lista=lista) 
        lstdict=[]
        lstdict2=[]
        cartaslist=[]
        #para cada carta buscaremos otras listas (de cambio/venta) donde aparece
        for elemento in items:          

           
            print(f"carta_id:{elemento.carta.id}/{elemento.carta.nombre}")
            #buscamos por la misma carta (mismo nombre, misma edicion, mismo tipo de borde)
            resultado1=ItemLista.objects.filter(carta=elemento.carta).exclude(lista__owner=elemento.lista.owner)
            #aca debemos buscar por nombre en caso de que este activado esto
            resultado_por_nombre=ItemLista.objects.filter(carta__nombre=elemento.carta.nombre).exclude(lista__owner=elemento.lista.owner)
            #print(resultado_por_nombre)
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
            if len(resultado_por_nombre)>1:
                sumar=True
                if elemento.carta.nombre in cartaslist:
                    sumar=False
                else:
                    cartaslist.append(elemento.carta.nombre)
                for r2 in resultado_por_nombre:
                    
                    #print(f"itemlista.carta.nombre:{r2.carta.nombre}")
                    #si la carta existe, me la salto
                    #print(f"lista:{r.lista.nombre},dueño:{r.lista.owner.name}")
                    #busco el indice donde exista un dict con name= r.lista.owner.name y lname=r.lista.nombre, si no existe: creo el dict y lo agrego
                    indice2=next((i for i, x in enumerate(lstdict2) if x["name"] == r2.lista.owner.name and  x["lname"] ==r2.lista.nombre and x["cname"] == r2.carta.nombre), None)
                    

                    #print(f"carta:{elemento.carta.nombre} la sumo?:{sumar} ")    
                    if indice2 is None:
                        new_elem2={
                            'name':r2.lista.owner.name ,
                            'lname':r2.lista.nombre,
                            'list_id':r2.lista.id,
                            'owner_id':r2.lista.owner.id,
                            'cname':r2.carta.nombre,
                            'qty':1
                        }
                        lstdict2.append(new_elem2)
                        indice2=0
                    else:
                        if sumar:
                        #considerar no repetir si ya esta otra carta con mismo nombre en la lista
                            lstdict2[indice2]['qty']+=1
                    
        #print(lstdict)
        context = {
            'saludo': 'Hola',
            "items":items,
            "lista_id":lista_id,
            "lista":lista,
            "duracion":dias,
            "resultado":lstdict,
            "resultado_por_nombre":lstdict2,
            "user":user
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
                "duracion":dias
            }
        return render(request, 'detalle_lista.html', context)
        new_carta=request.POST['new_card']

        nueva_lista=Listados.objects.create(owner=user,nombre=new_list,tipo='O')
        return redirect('/list/offer')

def share(request,lista_id):
    lista=Listados.objects.get(id=lista_id)
    items= ItemLista.objects.filter(lista=lista)
    usuario=lista.owner.name
    usuario_id=lista.owner.id
    ubicacion=lista.owner.ubicacion
    vista="imgs"
    user=""
    if 'user' in request.session:
        user= User.objects.get(id=request.session['user']['id'])
    if 'view' in request.GET:
        if request.GET['view'] == 'list' :
            vista="lista"

    nick=lista.owner.nick

    if request.method == "POST": #esta creando el nick en este caso
        nick_avail=User.objects.filter(nick=request.POST['nick']) 
        
        print(f"nick_avail:{nick_avail}")
        if nick_avail.count() == 0:
            print("no existe el nick y podemos crearlo")
            user.nick=request.POST['nick']
            user.save()
            nick=request.POST['nick']
            request.session['user']['nick']=nick

            #print( request.session['user']['nick'])
           
            messages.success(request, "Nick seteado con exito!")
        else :
            messages.warning(request, "Este Nick ya está siendo usado por otro usuario. Favor elija uno nuevo")

    #print(lista.owner.nick)

    context = {
            'saludo': 'Hola',
            "items":items,
            "lista_id":lista_id,
            "lista":lista,
            "usuario":usuario,
            "usuario_id":usuario_id,
            "vista":vista,
            "nickname":nick,
            "ubicacion":ubicacion,
            "user":user
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
    user= User.objects.get(id=request.session['user']['id'])
    if request.method == "POST":
        
        set=request.POST['set']
        carta_id=request.POST['card_id']        
        nombre=request.POST['nombre']
        set_name=request.POST['set_name']
        imagen=request.POST['img_small']
        img_small=imagen.split(',')
        #print(img_small)
        img_small=img_small[0]
        qty=request.POST['qty']
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
            new_item=ItemLista.objects.create(carta=carta,cantidad=qty,precio=0,lista=lista)
        else:
            messages.warning(request, "Carta ya existe en la lista.")
            print("La Carta ya existe.") #sumamos 1? 
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
                "user":user
            }
    return render(request, 'detalle_lista.html', context)

@login_required
def card_detail(request,item_id):
    item=ItemLista.objects.get(id=item_id)
    user= User.objects.get(id=request.session['user']['id'])
    #print(item)
    if request.method == "POST":
        form=ItemListaForm(request.POST,instance=item)
        if form.is_valid():
            user.save()
            messages.success(request, "Se ha actualizado con éxito!")
    else:
        form=ItemListaForm(instance=item)

    context = {
                "carta":item,
                "user":user,
                'form':form
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

def contacto(request):
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Su comentario ha sido enviado correctamente.")
            return redirect('/contacto')
    else:
        form=ComentarioForm()
    context = {
        'form':form,
    }
    return render(request, 'contacto.html', context)
