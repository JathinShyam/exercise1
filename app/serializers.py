from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import CustomUser, Country, State, City, CustomUserManager
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for Custom User model with additional validation
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True, 'min_length': 5}
        }
    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)
        return user
    
class CountrySerializer(serializers.ModelSerializer):
    """
    Serializer for Country model with nested state serialization
    """
    states = serializers.SerializerMethodField()
    my_user_name = serializers.SerializerMethodField()

    class Meta:
        model = Country
        # fields = [
        #     'id', 'name', 'country_code', 'curr_symbol', 
        #     'phone_code', 'my_user_name', 'states'
        # ]
        fields = '__all__'
        extra_kwargs = {
            'country_code': {
                'validators': [
                    UniqueValidator(queryset=Country.objects.all())
                ]
            },
            'phone_code': {
                'validators': [
                    UniqueValidator(queryset=Country.objects.all())
                ]
            }
        }

    def get_states(self, obj):
        """
        Retrieve nested states for a country
        """
        return StateSerializer(obj.states.all(), many=True).data

    def get_my_user_name(self, obj):
        """
        Retrieve username of associated user
        """
        return obj.my_user.email if obj.my_user else None

class StateSerializer(serializers.ModelSerializer):
    """
    Serializer for State model with nested city and country details
    """
    cities = serializers.SerializerMethodField()
    my_country_name = serializers.SerializerMethodField()
    my_country_user_name = serializers.SerializerMethodField()

    class Meta:
        model = State
        fields = [
            'id', 'name', 'state_code', 'gst_code', 
            'my_country_name', 'my_country_user_name', 'cities'
        ]
        # fields = '__all__'
        extra_kwargs = {
            'gst_code': {
                'validators': [
                    UniqueValidator(queryset=State.objects.all())
                ]
            }
        }

    def get_cities(self, obj):
        """
        Retrieve nested cities for a state
        """
        return CitySerializer(obj.cities.all(), many=True).data

    def get_my_country_name(self, obj):
        """
        Retrieve country name for the state
        """
        return obj.country.name

    def get_my_country_user_name(self, obj):
        """
        Retrieve username of country's associated user
        """
        return obj.country.my_user.email if obj.country.my_user else None

class CitySerializer(serializers.ModelSerializer):
    """
    Serializer for City model with state details
    """
    my_state_name = serializers.SerializerMethodField()

    class Meta:
        model = City
        # fields = [
        #     'id', 'name', 'city_code', 'phone_code', 
        #     'population', 'avg_age', 'num_of_adult_males', 
        #     'num_of_adult_females', 'my_state_name'
        # ]
        fields = '__all__'
        extra_kwargs = {
            'city_code': {
                'validators': [
                    UniqueValidator(queryset=City.objects.all())
                ]
            },
            'phone_code': {
                'validators': [
                    UniqueValidator(queryset=City.objects.all())
                ]
            }
        }

    def validate(self, attrs):
        """
        Custom validation to ensure population > sum of adult males and females
        """
        if attrs['population'] <= (attrs['num_of_adult_males'] + attrs['num_of_adult_females']):
            raise serializers.ValidationError(
                "Population must be greater than the sum of adult males and females"
            )
        return attrs

    def get_my_state_name(self, obj):
        """
        Retrieve state name for the city
        """
        return obj.state.name


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs