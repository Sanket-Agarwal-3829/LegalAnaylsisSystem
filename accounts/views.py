from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.hashers import make_password, check_password
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.shortcuts import render, redirect

from django.contrib.auth import login, authenticate #add this
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm #add this

def SignUpView(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful." )
            return render(request,'home.html')
        messages.error(request, "Unsuccessful registration. Invalid information.")
    return render(request,'registration/signup.html')

def login_me_in(request):
    print("Hello")
    if request.method == "POST":  
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return  redirect("/legal")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
        # print(request.POST)
        # print()
        # if CustomUser.objects.filter(email=request.POST['username']).exists():
        #     user = CustomUser.objects.get(email=request.POST['username'])
        #     if user.check_password(request.POST['password']):
        #         print(check_password(user.password, make_password(request.POST['password'])))
        #         return render(request,'home.html')        
    return render(request,'registration/login.html') 
