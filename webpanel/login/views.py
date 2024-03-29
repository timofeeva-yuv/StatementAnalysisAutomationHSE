from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/settings')
    error = ''
    if request.method == "POST":
        user = authenticate(request, username=request.POST['username'], password=request.POST['pass'])
        if user is not None:
            login(request, user)
            request.session['auth'] = 1
            return HttpResponseRedirect('/settings')
        else:
            error = "Invalid username and/or password"
    return render(request, "login.html", {'error': error})
