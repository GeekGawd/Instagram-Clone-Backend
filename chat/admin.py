from django.contrib import admin, auth
from django.db.models.fields import CharField
from .models import *

admin.site.register(Conversation)
admin.site.register(Message)