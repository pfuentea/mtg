from django.contrib import messages
from django.shortcuts import redirect, render
from .decorators import login_required
from .models.user import User
from .models.listados import Listados
from .models.contacto import Contacto
from .models.actividad import Actividad
from datetime import datetime, timedelta
from .forms.userForm import UserForm
from django.db.models import Q
import hashlib
import bcrypt
from django.core.mail import send_mail,EmailMultiAlternatives
from django.http import HttpResponse

def enviar_correo(request,token,correo):
    subject = 'Solicitud de cambio de clave CTMAGIC.CL'
    token_link='www.ctmagic.cl/user/password/new/1/'+token
    message = 'Pincha el siguiente link para cambiar tu contraseña:\n'+token_link
    email_from = 'contacto.ctmagic@gmail.com'
    destinatario=correo #'patricio.fuentealba.feliu@gmail.com'
    recipient_list = [destinatario]
    send_mail(subject, message, email_from, recipient_list)
    messages.success(request, "Revise cu correo para cambiar la clave")
    return HttpResponse('OK')

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
    hoy = datetime.now().date()
    limite = hoy - timedelta(days=14)

    listas_busqueda=Listados.objects.filter(owner=user, tipo='B',expiracion__gt=hoy)
    listas_venta=Listados.objects.filter(owner=user, tipo='O',expiracion__gt=hoy)
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
    resultado=''
    token=''
    if request.method == "POST":
        user=User.objects.filter(email=request.POST['email'])[0]
        
        if user:
            messages.success(request, "Contacto encontrado!")
            email=user.email
            #envio de mail con token            
            token=hashlib.md5(email.encode('utf-8')).hexdigest()
            result=enviar_correo(request,token,email)
            resultado='OK'
        else:
            messages.warning(request, "Este correo no existe para ningun usuario!")
    else:
        email=""
        user=""
    context={
        'email':email,
        'token':token,
        'user':user,
        "envio":resultado
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
    estado=""
    if request.method == "POST":
        usuario=User.objects.get(id=request.POST['user_id'])
        print(request.POST)
        #como ya pasó todas las otras validaciones, solo basta con que ambas claves sean iguales
        if request.POST['new_password'] == request.POST['new_password_confirm']:
            #cambiamos la clave
            password_encryp = bcrypt.hashpw(request.POST['new_password'].encode(), bcrypt.gensalt()).decode() 
            usuario.password=password_encryp
            messages.success(request, "Su contraseña ha sido cambiada con exito")
            estado="success"
        else:
            #repetimos l intento
            is_valid=True
            messages.warning(request, "Las claves no coinciden!")
            context={
                'is_valid':is_valid,  
                'user':usuario
            }
            return render(request, 'user/password_reset_email.html',context=context )
        context={            
            'user':usuario,
            "estado":estado
        }  
    return render(request, 'user/password_reset_email.html',context=context )


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