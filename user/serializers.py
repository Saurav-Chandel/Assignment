from rest_framework import serializers
from .models import *

class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields="__all__"
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            phone_otp=validated_data['phone_otp']
        )
        user.set_password(validated_data['password'])
        user.save()
        # print(user.id)

        #create profile instance.
        profile_obj=Profiles.objects.create(User_id=user.id)
        profile_obj.save()
        # print(profile_obj.User_id)

    
        return user


class DeviceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Devices
        fields="__all__"

    def create(self, validated_data):
        D=Devices.objects.create(**validated_data)
        return D

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = "__all__"
        # fields=("email","password")
        extra_kwargs = {
            "password": {"write_only": True},
        }        


class ProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profiles
        fields = "__all__"

    def create(self, validated_data):
        PR = Profiles.objects.create(**validated_data)
        return PR


class FriendRequestsSerializer(serializers.ModelSerializer):

    class Meta:
        model=FriendRequests
        fields="__all__"

    def create(self,validated_data):
        FR=FriendRequests.objects.create(**validated_data)
        return FR


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model=post
        fields="__all__"

    def create(self,validated_data):
        PO=post.objects.create(**validated_data)
        return PO
