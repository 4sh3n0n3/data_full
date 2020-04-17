from django.contrib import admin
from .forms import *
from .models import *

# Register your models here.


class ResearchesInLine(admin.TabularInline):
    model = Dataset.researches.through


@admin.register(Dataset)
class ContainerAdmin(admin.ModelAdmin):
    inlines = (ResearchesInLine, )
    exclude = ('researches', )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Research)
admin.site.register(ResearchGroup)
admin.site.register(CustomType)
