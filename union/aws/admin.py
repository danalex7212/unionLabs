from django.contrib import admin

# Register your models here.
from django.contrib import admin
from aws.models import User, OpenPorts, UsedPorts, OpenInstance, UsedInstance

admin.site.register(User)
admin.site.register(OpenPorts)
admin.site.register(UsedPorts)
admin.site.register(OpenInstance)
admin.site.register(UsedInstance)