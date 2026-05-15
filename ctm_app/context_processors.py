from .models.comentario import Comentario
from .models.user import User


def comentarios_no_leidos(request):
    try:
        user_session = request.session.get('user')
        if user_session:
            user = User.objects.get(id=user_session['id'])
            if user.role == 'admin':
                count = Comentario.objects.filter(leido=False).count()
                return {'comentarios_no_leidos': count}
    except Exception:
        pass
    return {'comentarios_no_leidos': 0}
