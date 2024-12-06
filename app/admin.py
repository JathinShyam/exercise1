from django.contrib import admin
from app.models import Country, State, City, CustomUser

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
