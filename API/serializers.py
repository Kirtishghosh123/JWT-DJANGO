from typing import Dict, Any
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from . import models
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = '__all__'


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)
        refresh = RefreshToken.for_user(self.user)
        data['refresh'] = str(refresh)
        return data

class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartProduct
        exclude = ['cart','product']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = '__all__'

    def create(self, validated_data):
        username = validated_data['username']
        user = CustomUser(username=username)
        password = validated_data['password']
        if password is not None:
            user.set_password(validated_data['password'])
            user.save()
            return user
        else:
            raise ValidationError('Give password')