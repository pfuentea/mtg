from django.contrib import messages
from django.shortcuts import redirect, render
from .decorators import login_required
from .models.user import User
from .models.mensaje import Mensaje



