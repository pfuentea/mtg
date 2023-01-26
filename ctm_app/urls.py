from django.urls import path
from . import views, auth , manage  ,user

urlpatterns = [
    path('', views.index),
    path('registro', auth.registro),
    path('login', auth.login),
    path('logout', auth.logout),

    path('list/hunt', views.list_hunt),
    path('list/offer', views.list_offer),
    
    path('list/offer/new', views.list_offer),
    path('list/hunt/new', views.list_hunt),

    path('list/edit/<int:list_id>', views.list_edit),

    path('list/<int:lista_id>', views.list_detail),
    path('list/add/<int:lista_id>', views.add_to_list),
    path('list/remove/<int:lista_id>', views.delete_list),
    path('list/search/', views.list_detail),

    path('list/view_all_hunt', views.view_all_hunt),
    

    path('list/share/<int:lista_id>', views.share),
    path('list/share/all', views.share_all),

    path('list/activar/<int:lista_id>', views.activar),
    path('list/desactivar/<int:lista_id>', views.desactivar),

    path('card/<int:item_id>/', views.card_detail),
    path('card/update/<int:item_id>', views.card_update), 
    path('card/remove/<int:lista_id>/<int:item_id>', views.remove_from_list),


    path('manage/card', views.list_hunt),
    path('manage/set', views.list_offer),
    path('manage/color', views.list_hunt),
    path('manage/type', views.list_offer),

    path('user/preferencias', user.preferencias),


    path('estadisticas', manage.stats), 

]
