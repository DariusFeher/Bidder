from users.forms import LoginUserForm
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from urllib3 import HTTPResponse

# Create your views here.

@login_required(login_url='login')
def homePage(request):
    return render(request, "home.html")