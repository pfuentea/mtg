from django.contrib import messages
from django.shortcuts import redirect, render
from .decorators import login_required
from .models import *

from .forms.userForm import UserForm



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