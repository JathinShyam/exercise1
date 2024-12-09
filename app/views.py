from django.shortcuts import render
from django.http import HttpResponse
import jwt, datetime

# REST Framework imports
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework import status

# Local imports
from exercise1 import settings
from .models import CustomUser, Country, State, City
from .serializers import (
    CustomUserSerializer,
    CountrySerializer,
    StateSerializer,
    CitySerializer,
)
from .pagination import ModelPagination


class RegisterView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []  # Disable permission

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

        content = {"message": f"Hello, {user.email}!"}
        return Response(content)


class LoginView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []  # Disable permission checks

    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        if not email or not password:
            raise AuthenticationFailed("Email and password are required!")

        user = CustomUser.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("User not found!")

        if not user.password == password:
            raise AuthenticationFailed("Incorrect password!")

        refresh = RefreshToken.for_user(user)
        access = AccessToken.for_user(user)

        response = Response()
        response.set_cookie(key="jwt", value=str(access), httponly=True)
        response.data = {"refresh": str(refresh), "access": str(access)}
        return response


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Extract the access token from the Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise AuthenticationFailed("Authorization header missing or invalid")

            access_token = auth_header.split(" ")[1]

            # Decode the access token to get the user ID
            decoded_token = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            user_id = decoded_token.get("user_id")

            # Get the refresh token for the user
            user = CustomUser.objects.get(id=user_id)
            refresh_token = RefreshToken.for_user(user)

            # Blacklist the refresh token
            refresh_token_obj = OutstandingToken.objects.get(token=str(refresh_token))
            BlacklistedToken.objects.create(token=refresh_token_obj)

            # Invalidate the access token by adding it to a blacklist or setting its expiration
            # Here, we will just delete the cookie and rely on the token expiration
            response = Response()
            response.delete_cookie("jwt")
            response.data = {"message": "success"}
            return response
        except OutstandingToken.DoesNotExist:
            return Response(
                {"error": "Token does not exist"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CustomUserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class CustomUserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class CountryListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = ModelPagination
    serializer_class = CountrySerializer

    def get_queryset(self):  # type: ignore
        return Country.objects.prefetch_related("states").filter(
            my_user=self.request.user
        )

    def create(self, request, *args, **kwargs):
        is_many = isinstance(
            request.data, list
        )  # Check if input is a list of countries

        if is_many:
            countries_data = request.data
        else:
            countries_data = [
                request.data
            ]  # Wrap single dictionary in a list for uniform processing

        created_countries = []  # To store created countries, their states, and cities

        for country_data in countries_data:
            states_data = country_data.pop(
                "states", []
            )  # Extract and remove states data from the country
            country_serializer = self.get_serializer(data=country_data)
            country_serializer.is_valid(raise_exception=True)
            country = country_serializer.save()  # Save the country

            created_states = []  # To store states created for this country

            # Process the states
            for state_data in states_data:
                cities_data = state_data.pop(
                    "cities", []
                )  # Extract and remove cities data from the state
                state_data["country"] = country.id  # Assign the country ID to the state
                state_serializer = StateSerializer(data=state_data)
                state_serializer.is_valid(raise_exception=True)
                state = state_serializer.save()  # Save the state

                # Process the cities
                for city_data in cities_data:
                    city_data["state"] = state.id  # Assign the state ID to the city
                    city_serializer = CitySerializer(data=city_data)
                    city_serializer.is_valid(raise_exception=True)
                    city_serializer.save()

                created_states.append(
                    state_serializer.data
                )  # Append the serialized state data

            # Add states to the country response data
            country_data_with_states = country_serializer.data
            country_data_with_states["states"] = created_states
            created_countries.append(
                country_data_with_states
            )  # Append the country data with states

        # Prepare the response
        if is_many:
            return Response(created_countries, status=status.HTTP_201_CREATED)
        else:
            return Response(created_countries[0], status=status.HTTP_201_CREATED)

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
    queryset = Country.objects.prefetch_related("states")

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

    def get_queryset(self):  # type: ignore
        return State.objects.prefetch_related("cities").all()

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)  # Check if the input is a list

        if is_many:
            states_data = request.data
        else:
            states_data = [
                request.data
            ]  # Wrap single dictionary in a list for uniform processing

        created_states = []  # To store created states and their cities

        for state_data in states_data:
            cities_data = state_data.pop(
                "cities", []
            )  # Extract and remove cities data from the state
            state_serializer = self.get_serializer(data=state_data)
            state_serializer.is_valid(raise_exception=True)
            state = state_serializer.save()  # Save the state

            # Process the cities
            for city_data in cities_data:
                city_data["state"] = state.id  # Assign the state ID to the city
                city_serializer = CitySerializer(data=city_data)
                city_serializer.is_valid(raise_exception=True)
                city_serializer.save()

            created_states.append(
                state_serializer.data
            )  # Append the serialized state data

        # Prepare the response
        if is_many:
            return Response(created_states, status=status.HTTP_201_CREATED)
        else:
            return Response(created_states[0], status=status.HTTP_201_CREATED)

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
    queryset = State.objects.prefetch_related("cities").all()

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

    def get_queryset(self):  # type: ignore
        return City.objects.all()

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

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
