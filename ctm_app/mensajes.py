from django.contrib import messages
from django.shortcuts import redirect, render,get_object_or_404
from .decorators import login_required
from .models.user import User
from .models.mensaje import Mensaje
from .models.contacto import Contacto


@login_required
def send(request):
    user= User.objects.get(id=request.session['user']['id'])
    mensajes=Mensaje.objects.filter(from_user=user)
    contactos=Contacto.objects.filter(usuario=user)
    if request.method == "POST":
        destinatario=User.objects.get(id=request.POST['destinatario_id'])
        new_msg=Mensaje.objects.create(from_user = user,to_user = destinatario, contenido=request.POST['mensaje'])
        messages.success(request, "Mensaje enviado con éxito!")
    context={
        'user':user,
        'mensajes':mensajes,
        'contactos':contactos
    }
    return render(request, 'mensajes/enviados.html', context=context )


@login_required
def get(request):
    user= User.objects.get(id=request.session['user']['id'])
    mensajes=Mensaje.objects.filter(to_user=user)
    context={
        'user':user,
        'mensajes':mensajes
    }
    return render(request, 'mensajes/recibidos.html', context=context )


@login_required
def VerMensaje(request, msg_id):
    previous_url = request.META.get('HTTP_REFERER').split('/')
    print(previous_url[-1])
    mensaje = get_object_or_404(Mensaje, pk=msg_id)
    user= User.objects.get(id=request.session['user']['id'])
    if previous_url[-1]=='get':
        mensajes=Mensaje.objects.filter(to_user=user)
    else:
        mensajes=Mensaje.objects.filter(from_user=user)

    context = {
        'user':user,
        'mensajes':mensajes,
        'mensaje': mensaje
        }
    
    if previous_url[-1]=='get':
        return render(request, 'mensajes/recibidos.html', context)
    return render(request, 'mensajes/enviados.html', context)

@login_required
def new(request):
    user= User.objects.get(id=request.session['user']['id'])

    mensajes=Mensaje.objects.filter(to_user=user)
    context={
        'user':user,
        'mensajes':mensajes
    }
    return render(request, 'mensajes/recibidos.html', context=context )