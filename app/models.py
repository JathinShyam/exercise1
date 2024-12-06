from uuid import uuid4
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


# Country Model
class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    country_code = models.CharField(max_length=3, unique=True)
    curr_symbol = models.CharField(max_length=5)
    phone_code = models.CharField(max_length=10, unique=True)
    my_user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)

    # Meta Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


# State Model
class State(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    state_code = models.CharField(max_length=10)
    gst_code = models.CharField(max_length=15, unique=True)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="states"
    )

    # Meta Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("country", "name")

    @property
    def country_name(self):
        return self.country.name

    @property
    def country_user_name(self):
        return self.country.my_user.email if self.country.my_user else None

    def __str__(self) -> str:
        return f"{self.name} - {self.country.name}"


# City Model
class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    city_code = models.CharField(max_length=10, unique=True)
    phone_code = models.CharField(max_length=10, unique=True)
    population = models.IntegerField()
    avg_age = models.FloatField()
    num_of_adult_males = models.IntegerField()
    num_of_adult_females = models.IntegerField()
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="cities")

    # Meta Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    @property
    def state_name(self):
        return self.state.name

    def clean(self):
        # Custom validation to ensure population > sum of adult males and females
        if self.population <= (self.num_of_adult_males + self.num_of_adult_females):
            raise ValidationError(
                "Population must be greater than the sum of adult males and females"
            )

    def __str__(self) -> str:
        return f"{self.name} - {self.state.name}"
