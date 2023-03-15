from django.contrib import messages
from django.shortcuts import redirect, render
from .decorators import login_required
from .models.user import User
from .models.listados import Listados
from .models.contacto import Contacto
from .models.actividad import Actividad

from .forms.userForm import UserForm

import hashlib

@login_required
def preferencias(request):
    
    user_id=request.session['user']['id']
    
        #print (f"User_id:{user_id}")
    user= User.objects.get(id=user_id)
   
    if request.method == "POST":
        form=UserForm(request.POST,instance=user)
        if form.is_valid():
            user.save()
            messages.success(request, "Se ha actualizado con éxito!")
    else:
        form=UserForm(instance=user)
    context={
        'user':user,
        'form':form
    }
    return render(request, 'user/preferencias.html', context=context )


def view(request,user_id):
    user= User.objects.get(id=user_id)
    listas_busqueda=Listados.objects.filter(owner=user, tipo='B')
    listas_venta=Listados.objects.filter(owner=user, tipo='O')
    n_contactos=Contacto.objects.filter(usuario=user)
    user_login=True
    if 'user' in request.session:
        usuario= User.objects.get(id=request.session['user']['id'])
    else:
        user_login=False

    contacto_valido=False
    if user_login:
        print("Vemos si es valido como nuevo contacto")
        if user != usuario: 
            print("User y usuario son distintos...")
            #busco si ya esta entre los contactos
            es_contacto=Contacto.objects.filter(usuario=usuario,contacto=user)
            if es_contacto.exists():
                print("usuario ya es contacto.")
            else:
                print("usuario puede ser contacto.")
                contacto_valido=True

    context={
        "user":user,
        "listas_busqueda":listas_busqueda,
        "listas_venta":listas_venta,
        "contacto_valido": contacto_valido,
        "user_login":user_login,
        "n_contactos":n_contactos
    }
    return render(request, 'user/view.html', context=context )

@login_required
def add_contacto(request,contacto_id):
    contacto= User.objects.get(id=contacto_id)    
        #print (f"User_id:{user_id}")
    user= User.objects.get(id=request.session['user']['id'])

    new_contacto=Contacto.objects.create(usuario=user,contacto=contacto)
    new_actividad=Actividad.objects.create(actor=user,accion="te ha agregado a sus contactos.",objetivo=contacto)
    messages.success(request, "Contacto agregado con éxito!")
    previous_url = request.META.get('HTTP_REFERER')
    return redirect(previous_url)

def password_change_request(request): #cuando el cambio en via correo
    
    token=''
    if request.method == "POST":
        user=User.objects.filter(email=request.POST['email'])[0]
        
        if user:
            messages.success(request, "Contacto encontrado!")
            email=user.email
            #envio de mail con token            
            token=hashlib.md5(email.encode('utf-8')).hexdigest()
            
        else:
            messages.warning(request, "Este correo no existe para ningun usuario!")
    
    context={
        'email':email,
        'token':token,
        'user':user
    }
    return render(request, 'user/password_reset_request.html',context=context )

def password_new(request,user_id,token):
    usuario=User.objects.get(id=user_id)
    email=usuario.email
    token_2= hashlib.md5(email.encode('utf-8')).hexdigest()
    
    is_valid = False
    if token == token_2:
        is_valid=True
        context={
            'is_valid':is_valid,  
            'user':usuario
        }
        print(f"t1:{token}" )
        print(f"t2:{token_2}" )
        return render(request, 'user/password_reset_email.html',context=context )
    else:
        return redirect('/inicio')
    

    

def password_change(request):#cuando el cambio es por las pref
    
            
    return render(request, 'password_reset_request.html')


'''
def cambiar_contraseña(request):
    if request.method == 'POST':
        form = CambiarContraseñaForm(request.POST)
        if form.is_valid():
            contraseña1 = form.cleaned_data['contraseña1']
            contraseña2 = form.cleaned_data['contraseña2']

            if contraseña1 == contraseña2:
                usuario = request.user  # obtiene el usuario actualmente logueado 
                usuario.set_password(contraseña1)  # cambia la contraseña del usuario 
                usuario.save()  # guarda los cambios en la base de datos 

                return redirect('login')

            else:
                messages.error(request, 'Las contraseñas no coinciden')

    else:
        form = CambiarContraseñaForm()

    return render(request, 'cambiar_contrasena.html', {'form': form})
    '''