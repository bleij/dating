from django.contrib import admin
from .models import User, Interaction, Match

admin.site.register(User)
admin.site.register(Interaction)
admin.site.register(Match)