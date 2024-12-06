from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import CustomUser, Country, State, City
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for Custom User model with additional validation
    """

    class Meta:
        model = CustomUser
        fields = ["id", "email", "password"]
        extra_kwargs = {
            "id": {"read_only": True},
            "password": {"write_only": True, "min_length": 5},
        }

    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)
        return user


class CountrySerializer(serializers.ModelSerializer):
    """
    Serializer for Country model with nested state serialization
    """

    name = serializers.CharField(max_length=100)
    country_code = serializers.CharField(max_length=3)
    curr_symbol = serializers.CharField(max_length=5)
    phone_code = serializers.CharField(max_length=10)
    states = serializers.SerializerMethodField()
    my_user_name = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = "__all__"
        extra_kwargs = {
            "country_code": {
                "validators": [UniqueValidator(queryset=Country.objects.all())]
            },
            "phone_code": {
                "validators": [UniqueValidator(queryset=Country.objects.all())]
            },
            "my_user": {"read_only": True},
        }

    def create(self, validated_data):
        user = self.context["request"].user
        return Country.objects.create(my_user=user, **validated_data)

    def get_states(self, obj):
        """
        Retrieve nested states for a country
        """
        return StateSerializer(obj.states.prefetch_related("cities"), many=True).data

    def get_my_user_name(self, obj):
        """
        Retrieve username of associated user
        """
        return obj.my_user.email if obj.my_user else None


class CitySerializer(serializers.ModelSerializer):
    """
    Serializer for City model with state details
    """

    name = serializers.CharField()
    city_code = serializers.CharField()
    phone_code = serializers.CharField()
    population = serializers.IntegerField()
    avg_age = serializers.FloatField()
    num_of_adult_males = serializers.IntegerField()
    num_of_adult_females = serializers.IntegerField()

    class Meta:
        model = City
        fields = "__all__"
        extra_kwargs = {}

    def validate(self, attrs):
        """
        Custom validation to ensure population > sum of adult males and females
        """
        if attrs["population"] <= (
            attrs["num_of_adult_males"] + attrs["num_of_adult_females"]
        ):
            raise serializers.ValidationError(
                "Population must be greater than the sum of adult males and females"
            )
        return attrs

    def validate_city_code(self, value):
        """
        Custom validation to ensure city_code is unique
        """
        if City.objects.filter(city_code=value).exists():
            raise serializers.ValidationError("City code must be unique")
        return value

    def validate_phone_code(self, value):
        """
        Custom validation to ensure phone_code is unique
        """
        if City.objects.filter(phone_code=value).exists():
            raise serializers.ValidationError("Phone code must be unique")
        return value

    def get_my_state__name(self, obj):
        """
        Retrieve state name for the city
        """
        return obj.state.name


class StateSerializer(serializers.ModelSerializer):
    """
    Serializer for State model with nested city and country details
    """

    cities = CitySerializer(many=True, required=False)
    name = serializers.CharField(max_length=100)
    state_code = serializers.CharField(max_length=10)
    gst_code = serializers.CharField(max_length=15)
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())
    my_country__name = serializers.SerializerMethodField()
    my_country__my_user__name = serializers.SerializerMethodField()

    class Meta:
        model = State
        fields = "__all__"
        extra_kwargs = {
            "gst_code": {"validators": [UniqueValidator(queryset=State.objects.all())]},
        }

    def get_cities(self, obj):
        """
        Retrieve nested cities for a state
        """
        return CitySerializer(obj.cities.all(), many=True).data

    def get_my_country__name(self, obj):
        """
        Retrieve country name for the state
        """
        return obj.country.name

    def get_my_country__my_user__name(self, obj):
        """
        Retrieve username of country's associated user
        """
        return obj.country.my_user.email if obj.country.my_user else None

    def create(self, validated_data):
        """
        Create a new state and associated cities.
        """
        # Extract cities data from the validated data
        cities_data = validated_data.pop("cities", [])

        # Create the State instance
        state = State.objects.create(**validated_data)

        # Now create the cities and associate them with the state
        for city_data in cities_data:
            City.objects.create(state=state, **city_data)

        return state


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs
