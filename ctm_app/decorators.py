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

def tier_required(allowed_tiers):
    from functools import wraps
    from ctm_app.models.user import User
    def decorator(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            if 'user' not in request.session:
                messages.warning(request, "Debe hacer Log In para continuar")
                return redirect('/login')
            
            user_id = request.session['user']['id']
            try:
                user = User.objects.get(id=user_id)
                if user.tier not in allowed_tiers:
                    messages.warning(request, f"Esta funcionalidad es exclusiva para cuentas {' o '.join(allowed_tiers)}.")
                    return redirect('/index')
            except User.DoesNotExist:
                messages.warning(request, "Usuario inválido.")
                return redirect('/login')
                
            return function(request, *args, **kwargs)
        return wrapper
    return decorator