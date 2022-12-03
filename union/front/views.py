from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.exceptions import AuthenticationFailed

import jwt , datetime
import requests
from django.apps import apps
from aws.serializers import UserSerializer
User = apps.get_model('aws', 'User')
UsedInstance = apps.get_model('aws', 'UsedInstance')
OpenPorts = apps.get_model('aws', 'OpenPorts')
UsedPorts = apps.get_model('aws', 'UsedPorts')

from aws.query import terminate_instance,delete_security_group
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
        raise AuthenticationFailed('Unauthenticated!')
        payload = jwt.decode(token, 'secret', algorithms=['HS256'],options={"verify_signature": False})
        request.delete_cookie('access')
        request.delete_cookie('refresh')
        instance = UsedInstance.objects.filter(id=payload['instanceId']).first()
        print(payload['instanceId'])
        usedPort = instance.port
        OpenPorts(usedPort.port).save()
        terminate_instance(instance.instance_id)
        delete_security_group(instance.sg_id)
        usedPort.delete()
        return render(request, 'login.html', {'title': 'Login'})
    
    user = User.objects.filter(id=payload['id']).first()
    instance = UsedInstance.objects.filter(id=payload['instanceId']).first()
    serializer = UserSerializer(user)
    print(serializer.data['name'])
    name = serializer.data['name']
    ip = instance.ip
    port = instance.port.port

    return render(request, 'home.html', {'title': 'Home','name': name, 'ip': ip, 'port': port})
    