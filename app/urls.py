from django.urls import path
from .views import CountryListCreateView, CountryRetrieveUpdateDestroyView, StateListCreateView, StateRetrieveUpdateDestroyView, CityListCreateView, CityRetrieveUpdateDestroyView, Home

urlpatterns = [
    path('', Home.as_view()),
    path('countries/', CountryListCreateView.as_view(), name='country-list-create'),
    path('countries/<uuid:pk>/', CountryRetrieveUpdateDestroyView.as_view(), name='country-detail'),
    path('states/', StateListCreateView.as_view(), name='state-list-create'),
    path('states/<uuid:pk>/', StateRetrieveUpdateDestroyView.as_view(), name='state-detail'),
    path('cities/', CityListCreateView.as_view(), name='city-list-create'),
    path('cities/<uuid:pk>/', CityRetrieveUpdateDestroyView.as_view(), name='city-detail'),

]
