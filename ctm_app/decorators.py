from django.shortcuts import redirect
from django.contrib import messages

def login_required(function):

    def wrapper(request, *args, **kwargs):
        if 'user' not in request.session :
            #print(f"IS_AUTH?{request.user.is_authenticated}"    )
            if request.user.is_authenticated:
                print("EXISTE!")
            else:
                messages.warning(request, "Debe hacer Log In para continuar")
                return redirect('/login')
        resp = function(request, *args, **kwargs)
        return resp
    
    return wrapper