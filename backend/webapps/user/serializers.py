
from rest_framework import serializers
from django.utils import timezone
from webapps.user.models import User

# class UserSerializer(serializers.Serializer):
#     username = serializers.CharField(max_length=32)
#     password = serializers.CharField(max_length=32)
#     create_time = serializers.DateTimeField(default=timezone.now())

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # 序列化除了passoword的其它字段
        fields = ['email_address','username','password','times','create_time','is_login'] 

        # # # 直接序列化model
        # fields = '__all__'