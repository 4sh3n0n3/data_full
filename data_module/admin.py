from django.contrib import admin
from .forms import *
from .models import *

# Register your models here.

admin.site.register(User, CustomUserAdmin)
admin.site.register(Research)
