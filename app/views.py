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

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)

        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            else:
                return serializer.errors
        except Exception as e:
            return Response("Exception: " + str(e), status=status.HTTP_400_BAD_REQUEST)


class CountryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CountrySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Country.objects.prefetch_related('states')

    def perform_update(self, serializer):
        try:
            if serializer.is_valid(raise_exception=True):
                super().perform_update(serializer)
            else:
                return serializer.errors
        except Exception as e:
            return Response("Exception: " + str(e), status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        return super().perform_destroy(instance)


class StateListCreateView(generics.ListCreateAPIView):
    serializer_class = StateSerializer
    pagination_class = ModelPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self): # type: ignore
        return State.objects.prefetch_related('cities').all()
    
    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)  # Check if the input is a list

        if is_many:
            states_data = request.data
        else:
            states_data = [request.data]  # Wrap single dictionary in a list for uniform processing

        created_states = []  # To store created states and their cities

        for state_data in states_data:
            cities_data = state_data.pop('cities', [])  # Extract and remove cities data from the state
            state_serializer = self.get_serializer(data=state_data)
            state_serializer.is_valid(raise_exception=True)
            state = state_serializer.save()  # Save the state

            # Process the cities
            for city_data in cities_data:
                city_data['state'] = state.id  # Assign the state ID to the city
                city_serializer = CitySerializer(data=city_data)
                city_serializer.is_valid(raise_exception=True)
                city_serializer.save()

            created_states.append(state_serializer.data)  # Append the serialized state data

        # Prepare the response
        if is_many:
            return Response(created_states, status=status.HTTP_201_CREATED)
        else:
            return Response(created_states[0], status=status.HTTP_201_CREATED)
        
    # def create(self, request, *args, **kwargs):
    #     is_many = isinstance(request.data, list)

    #     cities_data = request.data.get('cities', [])
    #     state_data = {key: value for key, value in request.data.items() if key != 'cities'}
    #     state_serializer = self.get_serializer(data=state_data, many=is_many)
    #     state_serializer.is_valid(raise_exception=True)

    #     if is_many:
    #         states = state_serializer.save()
    #     else:
    #         state = state_serializer.save()
        
    #     if cities_data:
    #         # Process each city in the 'cities' list
    #         for city_data in cities_data:
    #             # Assign the state to the city (set foreign key)
    #             city_data['state'] = state.id if not is_many else states[0].id  # Assuming only 1 state for now
    #             # Serialize and save each city
    #             city_serializer = CitySerializer(data=city_data)
    #             city_serializer.is_valid(raise_exception=True)
    #             city_serializer.save()

    #     # Get success headers for the response
    #     headers = self.get_success_headers(state_serializer.data if not is_many else [state_serializer.data for _ in states])

    #     # Return the response with the created data
    #     return Response(state_serializer.data if not is_many else [state_serializer.data for _ in states], 
    #                     status=status.HTTP_201_CREATED, headers=headers)



        # serializer = self.get_serializer(data=request.data, many=is_many)
        # serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            else:
                return serializer.errors
        except Exception as e:
            return Response("Exception: " + str(e), status=status.HTTP_400_BAD_REQUEST)

class StateRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = State.objects.prefetch_related('cities').all()

    def perform_update(self, serializer):
        try:
            if serializer.is_valid(raise_exception=True):
                super().perform_update(serializer)
            else:
                return serializer.errors
        except Exception as e:
            return Response("Exception: " + str(e), status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        return super().perform_destroy(instance)


class CityListCreateView(generics.ListCreateAPIView):
    serializer_class = CitySerializer
    pagination_class = ModelPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self): # type: ignore
        return City.objects.all()
    
    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)

        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            else:
                return serializer.errors
        except Exception as e:
            return Response("Exception: " + str(e), status=status.HTTP_400_BAD_REQUEST)


class CityRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CitySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = City.objects.all()

    def perform_update(self, serializer):
        try:
            if serializer.is_valid(raise_exception=True):
                super().perform_update(serializer)
            else:
                return serializer.errors
        except Exception as e:
            return Response("Exception: " + str(e), status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        return super().perform_destroy(instance)
