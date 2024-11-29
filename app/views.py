from webbrowser import get
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework import generics

from exercise1 import settings
from .models import CustomUser, Country, State, City
from .serializers import CustomUserSerializer, CountrySerializer, StateSerializer, CitySerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .pagination import ModelPagination
from rest_framework import (
    viewsets,
    mixins,
    status,
)

# class CustomUserPagination(PageNumberPagination):
#     page_size = 10
#     ordering = 'id'



class RegisterView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = [] # Disable permission
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class Home(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        content = {'message': f'Hello, {user.email}!'}
        return Response(content)


class LoginView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []  # Disable permission checks

    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        if not email or not password:
            raise AuthenticationFailed('Email and password are required!')

        user = CustomUser.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')
        
        if not user.password == password:
            raise AuthenticationFailed('Incorrect password!')
        
        refresh = RefreshToken.for_user(user)
        access = AccessToken.for_user(user)

        response = Response()
        response.set_cookie(key='jwt', value=str(access), httponly=True)
        response.data = {
            'refresh': str(refresh),
            'access': str(access)
        }
        return response

# class LogoutView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         try:
#             # Extract the access token from the Authorization header
#             auth_header = request.headers.get('Authorization')
#             if not auth_header or not auth_header.startswith('Bearer '):
#                 raise AuthenticationFailed('Authorization header missing or invalid')

#             access_token = auth_header.split(' ')[1]

#             # Decode the access token to get the refresh token
#             decoded_token = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
#             user_id = decoded_token.get('user_id')

#             # Get the refresh token for the user
#             user = CustomUser.objects.get(id=user_id)
#             refresh_token = RefreshToken.for_user(user)

#             # Blacklist the refresh token
#             from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
#             token = OutstandingToken.objects.get(token=str(refresh_token))
#             BlacklistedToken.objects.create(token=token)

#             response = Response()
#             response.delete_cookie('jwt')
#             response.data = {
#                 'message': 'success'
#             }
#             return response
#         except Exception as e:
#             return Response(status=status.HTTP_400_BAD_REQUEST)

# class gLogoutView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         try:
#             refresh_token = request.data["refresh"]
#             token = RefreshToken(refresh_token)
#             token.blacklist()

#             response = Response()
#             response.delete_cookie('jwt')
#             response.data = {
#                 'message': 'success'
#             }
#             return response
#         except Exception as e:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
    

class CustomUserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    # pagination_class = CustomUserPagination


class CustomUserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class CountryListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = ModelPagination
    serializer_class = CountrySerializer

    def get_queryset(self): # type: ignore
        return Country.objects.prefetch_related('states').filter(my_user=self.request.user)
    

class CountryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CountrySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Country.objects.prefetch_related('states')


class StateListCreateView(generics.ListCreateAPIView):
    serializer_class = StateSerializer
    pagination_class = ModelPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self): # type: ignore
        return State.objects.prefetch_related('cities').all()


    # def list(self, request, *args, **kwargs):
    #     queryset = 
    #     serializer = StateSerializer(queryset, many=True)
    #     return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class StateRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = State.objects.prefetch_related('cities').all()


class CityListCreateView(generics.ListCreateAPIView):
    serializer_class = CitySerializer
    pagination_class = ModelPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # def list(self, request, *args, **kwargs):
    #     queryset = City.objects.all()
    #     serializer = CitySerializer(queryset, many=True)
    #     return Response(serializer.data)

    def get_queryset(self): # type: ignore
        return City.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CityRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CitySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = City.objects.all()

    # def get_queryset(self):
    #     return City.objects.filter(user=self.request.user)