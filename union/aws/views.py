import email
from email import message
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import User
import jwt , datetime

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
        

        access_payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        refresh_payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'iat': datetime.datetime.utcnow()
        }

        access_token = jwt.encode(access_payload, 'secret', algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, 'secret', algorithm='HS256')

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
    
class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        response.data = {'message': 'success'}
        return response