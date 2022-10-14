from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.exceptions import AuthenticationFailed

import jwt , datetime
import requests
from django.apps import apps
User = apps.get_model('aws', 'User')
# Create your views here.
def index(request):
    
    return render(request, 'login.html', {'title': 'Login'})

def login(request):
    if request.method == 'GET':
        token = request.COOKIES.get('access')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
        user = User.objects.filter(id=payload['id']).first()
        print(user)
        return render(request, 'home.html', {'title': 'Home'})