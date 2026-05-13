from django.contrib import messages
from django.shortcuts import redirect, render
import bcrypt
from .models.user import User

def logout(request):
    if 'user' in request.session:
        del request.session['user']
    
    return redirect("/")
    

def login(request):
    if request.method == "POST":
        user = User.objects.filter(email=request.POST['email'])
        if user:
            log_user = user[0]
            print(f"DarkMode:{log_user.modo_oscuro}")

            valid = False
            if log_user.check_password(request.POST['password']):
                valid = True
            else:
                try:
                    if bcrypt.checkpw(request.POST['password'].encode(), log_user.password.encode()):
                        log_user.set_password(request.POST['password'])
                        log_user.save()
                        valid = True
                except ValueError:
                    pass

            if valid:

                user = {
                    "id" : log_user.id,
                    "name": log_user.name,
                    "email": log_user.email,
                    "role": log_user.role,
                    "nick":log_user.nick,
                    "ubicacion":log_user.ubicacion,
                    "modo_oscuro":log_user.modo_oscuro
                }

                request.session['user'] = user
                messages.success(request, "Logueado correctamente.")
                return redirect("/index")
            else:
                messages.error(request, "Password o Email  incorrectos.")
        else:
            messages.error(request, "Email o password incorrectos.")



        return redirect("/login")
    else:
        if 'user' in request.session:
            messages.success(request, "Ya habías ingresado anteriormente.")
            return redirect('/index')
        return render(request, 'login.html')


def registro(request):
    if request.method == "POST":

        existe_email=User.objects.filter(email=request.POST['email'])
        print(f"correos_iguales:{len(existe_email)}" )
        if len(existe_email) > 0: #correo ya existe!
            messages.warning(request, "Este correo ya existe! Ingrese por Login.")
            return redirect("/registro")
        #errors = User.objects.validador_basico(request.POST)
        # print(errors)
        
        '''
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            
            request.session['register_name'] =  request.POST['name']
            request.session['register_email'] =  request.POST['email']

        else:
        '''
        request.session['register_name'] = ""
        request.session['register_email'] = ""

        usuario_nuevo = User.objects.create_user(
            name = request.POST['name'],
            email=request.POST['email'],
            password=request.POST['password'],
            role=request.POST['role']
        )

        messages.success(request, "El usuario fue agregado con exito.")
        

        request.session['user'] = {
            "id" : usuario_nuevo.id,
            "name": f"{usuario_nuevo.name}",
            "email": usuario_nuevo.email,
            "modo_oscuro":usuario_nuevo.modo_oscuro
        }
        return redirect("/index")

        #return redirect("/registro")
    else:
        return render(request, 'registro.html')
