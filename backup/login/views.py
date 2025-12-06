from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate , login, logout
from django.contrib import messages
import re
from .models import *

def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request,'about.html')


def register(request):
    if request.method == "POST":
        profile = request.FILES.get('profile')
        fullname = request.POST.get('fullname')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return redirect('register')

        result = User.objects.create(profile=profile, phone=phone, fullname=fullname, 	email=email, password=make_password(password2))
        result.save()


    return render(request,'register.html')



def signin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(email=email,password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'login.html')



def signout(request):
    logout(request)
    return redirect('home')

def offences(request):
    return render(request,'offences.html')
