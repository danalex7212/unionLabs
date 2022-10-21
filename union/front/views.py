from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.exceptions import AuthenticationFailed

import jwt , datetime
import requests
from django.apps import apps
from aws.serializers import UserSerializer
User = apps.get_model('aws', 'User')
# Create your views here.
def index(request):
    
    return render(request, 'register.html', {'title': 'Register'})

def login(request):
    
    if request.method == 'GET':
        return render(request, 'login.html', {'title': 'Login'})

def home(request):
    token = request.COOKIES.get('access')

    if not token:
        return render(request, 'login.html', {'title': 'Login'})

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return render(request, 'login.html', {'title': 'Login'})
    
    user = User.objects.filter(id=payload['id']).first()
    serializer = UserSerializer(user)
    print(serializer.data['name'])
    name = serializer.data['name']
    return render(request, 'home.html', {'title': 'Home','name': name})
    