import email
from email import message
from django.shortcuts import render
from rest_framework.views import APIView

from aws.query import change_securtiy_group, create_instance,terminate_instance,delete_security_group,run_command
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import User
import jwt , datetime
import time


import boto3
import urllib.request
import sys
from urllib import response
from aws.query import create_security_group
from aws.query import get_public_ip
from botocore.exceptions import ClientError

from aws.models import User
from aws.models import OpenPorts
from aws.models import UsedPorts
from aws.models import OpenInstance
from aws.models import UsedInstance

from django.db.models import Max

import asyncio
# Create your views here.
def index(request):
    # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    # if x_forwarded_for:
    #     ip = x_forwarded_for.split(',')[0]
    # else:
    #     ip = request.META.get('REMOTE_ADDR')
    # print(ip)
    return render(request, 'login.html', {'title': 'Login'})

def login(request):
    if request.method == 'POST':
        # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        # if x_forwarded_for:
        #     ip = x_forwarded_for.split(',')[0]
        # else:
        #     ip = request.META.get('REMOTE_ADDR')
        # print(ip)
        return render(request, 'login.html', {'title': 'Login'})

class RegisterView(APIView):
    def post(self, request):
        
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
        
class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        print(email)
        print(password)
        
        
        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')
        
        ip_response = urllib.request.urlopen('http://checkip.amazonaws.com')
        current_ip_address = ip_response.read().decode('utf-8').strip()
        # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        # if x_forwarded_for:
        #     current_ip_address = x_forwarded_for.split(',')[0]
        # else:
        #     current_ip_address = request.META.get('REMOTE_ADDR')
        # print(current_ip_address)
        
        #security_group_id = create_security_group(f'client{user.pk}',port.port,current_ip_address)
        
        open_instance = OpenInstance.objects.all()[0]
        print("OPenInstance: ", open_instance)
        open_instance_id = open_instance.instance_id
        open_instance_ip = get_public_ip(open_instance_id)
        print("OPenInstance id : ", open_instance_id)
        print("OPenInstance ip : ", open_instance_ip)
        change_securtiy_group(open_instance.sg_id,current_ip_address,open_instance.port.port)
        print("changed security group")
        #run_command(open_instance_id,open_instance.port.port)
        
        use_instance = UsedInstance(name=open_instance.name,instance_id=open_instance_id,ip=open_instance_ip,sg_id=open_instance.sg_id,port=open_instance.port)
        use_instance.save()
        
        print("Used Instance created in  table")

        try:
            numOpenInst =  OpenInstance.objects.latest('pk').pk
        except OpenInstance.DoesNotExist:
            numOpenInst =  0

        open_port = OpenPorts.objects.all()[0]
        new_port = UsedPorts(port=open_port.port)
        new_port.save()
        #new_sg_id = create_security_group(f'client{numOpenInst+1}')
        #new_instance_id = create_instance(f'client{numOpenInst+1}',new_sg_id,new_port.port)
        message = 'createInstance '+str(numOpenInst)+' '+str(new_port.port)+' '+str(new_port.pk)
        message +=' '+str(int(time.time()*10e6))
        print(message)
        sqsClient = boto3.client('sqs')
        response = sqsClient.send_message(
            QueueUrl='https://queue.amazonaws.com/780492718645/createQueue.fifo',
            MessageBody=message,
            MessageGroupId='unionLabs'
        )
        print(response)
        print("new instance and security group created")

        # OpenInstance(name=f'client{numOpenInst+1}',instance_id=new_instance_id,sg_id=new_sg_id,port=new_port).save()
        open_port.delete()
        open_instance.delete()
        print("open instance created in table")
        access_payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
            'iat': datetime.datetime.utcnow(),
            'instanceId': use_instance.id
            
        }
        refresh_payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'iat': datetime.datetime.utcnow(),
            'instanceId': use_instance.id
        }

        access_token = jwt.encode(access_payload, 'secret', algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, 'secret', algorithm='HS256')
        print("tokens created")
        response = Response()
        response.set_cookie(key='access', value=access_token, httponly=True)
        response.set_cookie(key='refresh', value=refresh_token, httponly=True)
        response.data = {"message": "success"}

        return response

class UserView(APIView):
    def get(self,request):
        token = request.COOKIES.get('access')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)

class RefreshView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh')

        if not refresh_token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(refresh_token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise AuthenticationFailed('User not found!')

        access_payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
            'iat': datetime.datetime.utcnow(),
            'instanceId': payload['instanceId']
        }
        refresh_payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'iat': datetime.datetime.utcnow(),
            'instanceId': payload['instanceId']
        }
        access_token = jwt.encode(access_payload, 'secret', algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='access', value=access_token, httponly=True)
        response.set_cookie(key='refresh', value=refresh_token, httponly=True)
        response.data = {"message": "success"}
        print("refresh view")
        return response
    
class LogoutView(APIView):
    def post(self, request):
        response = Response()
        token = request.COOKIES.get('access')

        payload = jwt.decode(token, 'secret', algorithms=['HS256'],options={"verify_signature": False})
        instance = UsedInstance.objects.filter(id=payload['instanceId']).first()
        print(instance)
        usedPort = instance.port
        print(usedPort)
        OpenPorts(port=usedPort.port).save()
        deleteInstanceMessage = 'deleteInstance '+instance.instance_id
        deleteInstanceMessage +=' '+str(int(time.time()*10e6))

        deleteSgMessage = 'deleteSg '+instance.sg_id
        deleteSgMessage +=' '+str(int(time.time()*10e6))
        
        sqsClient = boto3.client('sqs')
        sqsResponse = sqsClient.send_message(
                    QueueUrl='https://queue.amazonaws.com/780492718645/createQueue.fifo',
                    MessageBody=deleteInstanceMessage,
                    MessageGroupId='unionLabs'
                )
        print(sqsResponse)
        sqsResponse = sqsClient.send_message(
                    QueueUrl='https://sqs.us-east-1.amazonaws.com/780492718645/deleteSg.fifo',
                    MessageBody=deleteSgMessage,
                    MessageGroupId='unionLabs'
                )
        print(sqsResponse)
        #terminate_instance(instance.instance_id)
        #asyncio.run(delete_security_group(instance.sg_id))
        usedPort.delete()
        
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        response.data = {'message': 'success'}
        return response