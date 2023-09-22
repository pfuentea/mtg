from django.shortcuts import redirect


def login_required(function):

    def wrapper(request, *args, **kwargs):
        if 'user' not in request.session :
            print(request.user.is_authenticated)
            if request.user.is_authenticated:
                print("EXISTE!")
            else:
                return redirect('/login')
        resp = function(request, *args, **kwargs)
        return resp
    
    return wrapper