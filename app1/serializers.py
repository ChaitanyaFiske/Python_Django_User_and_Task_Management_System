
from rest_framework import serializers
from .models import user_detail, task_detail

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_detail
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = task_detail
        fields = '__all__'
