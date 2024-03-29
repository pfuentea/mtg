from operator import itemgetter
from django.contrib import messages
from django.shortcuts import redirect, render,get_object_or_404
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
from .forms.listaForm import ListaForm
from .models.mensaje import Mensaje

from datetime import datetime, timedelta,timezone
from django.http import HttpRequest
import pytz
from itertools import groupby
from django.contrib.auth import logout

def group_func(item):
    return item['name'], item['lname'], item['list_id'], item['owner_id']


def landing(request):
    referer = request.META.get('HTTP_REFERER', None)

    if referer:
        print(f"Ref:{referer}")

    if request.user.is_authenticated:
        print(request.user.first_name)
        
        if len(request.user.name) == 0:
            print("Nombre vacio...actualizando!")
            usuario = User.objects.get(pk=request.user.id)
            usuario.name=request.user.first_name+' '+request.user.last_name
            usuario.save()
        else:
            print("Ya tiene")
        return redirect('/index')

        #usuario=User.get_user(email=request.user['email'])
        #print(f"U:{usuario.first_name}")

    context = {
               
            }
    return render(request, 'landing.html', context=context )

@login_required
def index(request):
    print("INDEX:init")
    if 'user' in request.session:
        user= User.objects.get(id=request.session['user']['id'])
    else:
        #print(request.user.email)
        user= User.objects.filter(email=request.user.email)[0]
        request.session['user'] = {
            "id" : user.id,
            "name": f"{user.name}",
            "email": user.email,
            "modo_oscuro":user.modo_oscuro
        }


    listas_hunt= Listados.objects.filter(owner=user,tipo='B').order_by('-updated_at')[:10]
    listas_off= Listados.objects.filter(owner=user,tipo='O').order_by('-updated_at')[:10]
    last_act=Actividad.objects.filter(objetivo__isnull=True).order_by('-updated_at')[:10]
    last_act_propia=Actividad.objects.filter(objetivo=user).order_by('-updated_at')[:10]
    
    recibidos=Mensaje.objects.filter(to_user=user).order_by('-updated_at')[:10]

    print(f"u_act:{last_act_propia}")
    context = {
            'saludo': 'Hola',
            "listas_hunt":listas_hunt, 
            "listas_off":listas_off,
            "actividades":last_act,
            "user":user,
            "last_act_propia":last_act_propia,
            "recibidos":recibidos
        }
    #print (f"USer:{request.session['user']}")
    return render(request, 'index.html', context=context )

@login_required
def list_hunt(request):
    user_id=request.session['user']['id']
        #print (f"User_id:{user_id}")
    user= User.objects.get(id=user_id)
    
    if request.method == "GET":
        
        listas= Listados.objects.filter(owner=user,tipo='B').order_by('-updated_at')
        result=[]
        for l in listas:
            estado="Activa"
            ahora = datetime.now(timezone.utc) #datetime.datetime
            fecha_exp=l.expiracion.replace(tzinfo=pytz.UTC)
            diff= fecha_exp - ahora        
            dias=divmod(diff.total_seconds() ,24 * 60 * 60 )[0] 
            print(f"{l.expiracion},diff:{diff},dias:{dias}")
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
        
        listas= Listados.objects.filter(owner=user,tipo='O').order_by('-updated_at')
        result=[]
        for l in listas:
            
            estado="Activa"
            ahora = datetime.now(timezone.utc) #datetime.datetime
            fecha_exp=l.expiracion.replace(tzinfo=pytz.UTC)
            diff= fecha_exp - ahora        
            dias=divmod(diff.total_seconds() ,24 * 60 * 60 )[0] 
            print(f"{l.expiracion},diff:{diff},dias:{dias}")
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
        dos_semanas= datetime.now(timezone.utc) + timedelta(days=14)
        print(f"2sem:{dos_semanas}")
        nueva_lista=Listados.objects.create(owner=user,nombre=new_list,tipo='O',referencia_web='',referencia_precio=0,expiracion=dos_semanas)
        # esta accion registra una actividad
        mensaje=f" ha creado la lista para ofrecer"
        new_act=Actividad.objects.create(actor=user,accion=mensaje,lista=nueva_lista)       

        return redirect('/list/offer')

@login_required
def list_detail(request,lista_id):
    print("Inicio:list_detail")
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
        lstdict=[] # donde se guardan las cartas que estan en la lista exacta 
        lstdict2=[] # donde se guardan las cartas por nombre
        cartaslist=[] #donde se guardan las cartas por nombre
        #para cada carta buscaremos otras listas (de cambio/venta) donde aparece
        for card_in_list in items:
            print(f"carta_id:{card_in_list.carta.id}/{card_in_list.carta.nombre}")
            #buscamos por la misma carta (mismo nombre, misma edicion, mismo tipo de borde)
            resultado_exacto=ItemLista.objects.filter(carta=card_in_list.carta,lista__tipo='O').exclude(lista__owner=card_in_list.lista.owner)
            #aca debemos buscar por nombre en caso de que este activado esto
            resultado_por_nombre=ItemLista.objects.filter(carta__nombre=card_in_list.carta.nombre,lista__tipo='O').exclude(lista__owner=card_in_list.lista.owner)
            if len(resultado_exacto) >0:
                #print("Encontre la carta en otra lista!")
                for r in resultado_exacto:
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
            
            if len(resultado_por_nombre)>0:
                sumar=True
                if card_in_list.carta.nombre in cartaslist:
                    sumar=False
                else:
                    cartaslist.append(card_in_list.carta.nombre)
                for r2 in resultado_por_nombre:
                    
                    #print(f"itemlista.carta.nombre:{r2.carta.nombre}")
                    #si la carta existe, me la salto
                    #print(f"lista:{r.lista.nombre},dueño:{r.lista.owner.name}")
                    #busco el indice donde exista un dict con name= r.lista.owner.name y lname=r.lista.nombre, si no existe: creo el dict y lo agrego
                    indice2=next((i for i, x in enumerate(lstdict2) if x["name"] == r2.lista.owner.name and  x["lname"] ==r2.lista.nombre and x["cname"] == r2.carta.nombre), None)
                    
                    print(f"indice2:{indice2}")
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
                    
        print(lstdict2)
        # Ordenar la lista por los campos de agrupación
        lstdict2.sort(key=group_func)

        # Lista para almacenar los resultados
        resultados = []

        # Iterar sobre los grupos y obtener el total de cada uno
        for group, items2 in groupby(lstdict2, key=group_func):
            total = sum(item['qty'] for item in items2)
            resultados.append({'name': group[0], 'lname': group[1], 'list_id': group[2], 'owner_id': group[3], 'qty': total})

        # Imprimir los resultados
        #print(resultados)
        #print(f"lista:{lista}")
        context = {
            'saludo': 'Hola',
            "items":items,
            "lista_id":lista_id,
            "lista":lista,
            "duracion":dias,
            "resultado":lstdict,
            "resultado_por_nombre":resultados,
            "user":user
        }
        return render(request, 'lista_detalle.html', context)
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
        return render(request, 'lista_detalle.html', context)
        new_carta=request.POST['new_card']

        nueva_lista=Listados.objects.create(owner=user,nombre=new_list,tipo='O')
        return redirect('/list/offer')

def compare(request,lista_origen,lista_destino,view='imgs'):
    resultado=[]
    if 'user' in request.session:
        user= User.objects.get(id=request.session['user']['id'])
    else:
        user=""
    origen=Listados.objects.get(id=lista_origen)
    destino=Listados.objects.get(id=lista_destino)
    items_origen= ItemLista.objects.filter(lista=origen) 
    items_destino= ItemLista.objects.filter(lista=destino) 
    nombres_destino = [item.carta.nombre for item in items_destino]
    #print(nombres_destino)
    nombres_comunes = [carta_or.carta.nombre for carta_or in items_origen if any(carta_or.carta.nombre == nombre for nombre in nombres_destino)]
    for carton in items_origen:
        if carton.carta.nombre in nombres_comunes:
            resultado.append(carton)
    
    total_coincidencias=len(resultado)
    request.session['view_compare']=view
    vista=request.session['view_compare']
    
    context={
        "user":user,
        "items":resultado,
        "vista":vista,
        "total_coincidencias":total_coincidencias,
        "lista_origen":origen,
        "lista_destino":destino
    }
    return render(request, 'compare.html', context)

def share(request,lista_id):
    try:
        lista=Listados.objects.get(id=lista_id)
        
        usuario=lista.owner.name
        usuario_id=lista.owner.id
        ubicacion=lista.owner.ubicacion
        vista="imgs"
        user=""
        items= ItemLista.objects.filter(lista=lista).order_by('carta__nombre')
        fecha1=lista.updated_at
        iten_newest=lista.items.latest('updated_at')
        fecha2=iten_newest.updated_at
        last_act=max(fecha1,fecha2)
        #print(f"fecha1:{fecha1}, fecha2:{fecha2}, max:{last_act}")
        
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
                "user":user,
                "last_act":last_act
            }


        return render(request, 'share.html', context)
    except ItemLista.DoesNotExist:
        print("No hay elementos en la lista")
        error_except="NoItems"
    except Exception as e:
        error_except="NoList"
        usuario_id=""
        print('%s' % type(e))
    context = {
        "error_except":error_except,
        "usuario_id":usuario_id
    }
    return render(request, 'share_no_existe.html', context)
    
    
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
    user= User.objects.get(id=request.session['user']['id'])
    #form=ListaForm(instance=lista)

    if request.method == 'POST':
        #print(request.POST)
        form = ListaForm(request.POST,instance=lista)
        if form.is_valid():
            form.save()
            messages.success(request, "Lista modificada con exito.")
        else:
            print(form.errors)
            messages.warning(request, "Algo pasa.")
            #messages.success(request, "Su comentario ha sido enviado correctamente.")
            #return redirect('/contacto')
    else:
        form=ListaForm(instance=lista)

    '''
    if request.method == "POST":
        lista.nombre=request.POST['nombre']
        lista.tipo=request.POST['tipo']
        lista.referencia_precio=request.POST['ref_precio']
        lista.referencia_web=request.POST['ref_web']
        lista.descripcion=request.POST['descripcion']
        lista.save()
        messages.success(request, "Lista modificada con exito.")
        '''

    context = {
        'saludo': 'Hola',
        "lista":lista,
        "lista_id":list_id,
        "usuario":usuario,
        "user":user,
        "form":form
        }
    return render(request, 'lista_update.html', context)

@login_required
def add_to_list(request,lista_id):
    lista=Listados.objects.get(id=lista_id)
    user= User.objects.get(id=request.session['user']['id'])
    ahora = datetime.now(timezone.utc) #datetime.datetime
    fecha_exp=lista.expiracion.replace(tzinfo=pytz.UTC)
    diff= fecha_exp - ahora   
    dias=divmod(diff.total_seconds() ,24 * 60 * 60 )[0]

    if request.method == "POST":
        print(request.POST)
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
                "user":user,
                "duracion":dias,
            }
    return render(request, 'lista_detalle.html', context)

@login_required
def card_detail(request,item_id):
    print("Inicio:card_detail")
    #item=ItemLista.objects.get(id=item_id)
    item_lista = get_object_or_404(ItemLista, pk=item_id)
    user= User.objects.get(id=request.session['user']['id'])
    #print(item)
    
    if request.method == "POST":
        print(request.POST)
        form=ItemListaForm(request.POST,instance=item_lista)
        if form.is_valid():
            item_lista = form.save(commit=False)
            item_lista.save()
            messages.success(request, "Se ha actualizado con éxito!")
        else:
            print(form.errors)
            messages.warning(request, "Algo va mal")
    else:
        form=ItemListaForm(instance=item_lista)

    context = {
                "carta":item_lista,
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
    previous_url = request.META.get('HTTP_REFERER')
    return redirect(previous_url)

@login_required
def view_all_hunt(request):
    user_id=request.session['user']['id']
        #print (f"User_id:{user_id}")
    user= User.objects.get(id=user_id)
    
    items= ItemLista.objects.filter(lista__owner=user,lista__tipo='B')
    context = {
                
                "items":items,
                "search":"",
                "tipo":'B',
                "user":user
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

def custom_logout(request):
    logout(request)
    messages.success(request, "Sessión finalizada correctamente.")
    # Renderiza tu template personalizado
    return render(request, 'accounts/logged_out.html')

