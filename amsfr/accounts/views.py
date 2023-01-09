from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def login_user(request):
    context = {}
    template = 'accounts/login.html'

    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        if user is None:
            context = {"error":"Invalid username or password."}
            return render(request, template, context)
        login(request, user)
        messages.success(request, "Login successfully!")
        return redirect('home')
    return render(request, template, context)

def logout_user(request):
    context = {}
    template = "accounts/logout.html"
    if request.method == 'POST':
        logout(request)
        messages.success(request, "Logout successfully!")
        return redirect('login')
    # return redirect('login')
    return render(request, template, context)
    