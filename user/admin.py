from django.contrib import admin
from user.models import *
# Register your models here.


admin.site.register(User)
admin.site.register(Devices)
admin.site.register(Profiles)
admin.site.register(FriendRequests)
admin.site.register(post)
admin.site.register(Field)
admin.site.register(Form)
admin.site.register(UserDetails)