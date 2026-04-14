from django.contrib import admin
from .models import *

# Register your models here.

class userclass(admin.ModelAdmin):
    list_display = ['id', 'Name', 'email', 'mobile', 'city']

admin.site.register(user_detail, userclass)


class task_class(admin.ModelAdmin):
    list_display = ['fk_user', 'taskname', 'taskdetails', 'status', 'assigndate', 'duedate', 'totaldays', 'completion_date', 'remaining_days']

admin.site.register(task_detail, task_class)
