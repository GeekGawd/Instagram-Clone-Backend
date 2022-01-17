from os import stat, write
from django.contrib.auth import get_user_model, authenticate
from django.db.models import fields
from django.core.exceptions import ValidationError
import re
from django.http import request
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from django.forms.models import model_to_dict
from socialuser.models import Profile
from core.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5, 'required': True, 'error_messages': {"required": "Password needed"}},
                        'email': {'required': True, 'error_messages': {"required": "Email field may not be blank."}},
                        'name': {'required': True, 'error_messages': {"required": "Name field may not be blank."}},
                        }

    def validate_password(self, password):
        if not re.findall('\d', password):
            raise ValidationError(
                _("The password must contain at least 1 digit, 0-9."),
                code='password_no_number',
            )
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                _("The password must contain at least 1 uppercase letter, A-Z."),
                code='password_no_upper',
            )
        if not re.findall('[a-z]', password):
            raise ValidationError(
                _("The password must contain at least 1 lowercase letter, a-z."),
                code='password_no_lower',
            )

        return password

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        Profile.objects.create(user=user)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, password):
        if not re.findall('\d', password):
            raise ValidationError(
                ("The password must contain at least 1 digit, 0-9."),
                code='password_no_number',
            )
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                ("The password must contain at least 1 uppercase letter, A-Z."),
                code='password_no_upper',
            )
        if not re.findall('[a-z]', password):
            raise ValidationError(
                ("The password must contain at least 1 lowercase letter, a-z."),
                code='password_no_lower',
            )

        return password
    

class AuthTokenSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True, error_messages={
                                  "required": "Email field may not be blank."})
    password = serializers.CharField(write_only=True, min_length=5)

    class Meta:
        model = User
        fields = ['email', 'access', 'refresh', 'password']

    def to_representation(self, instance):
        data = super(AuthTokenSerializer, self).to_representation(instance)
        name = User.objects.get(email=instance['email']).name
        # name = User.objects.get(email=self.email)
        data['name'] = name
        return data

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            raise ValidationError(
                'Unable to authenticate with provided credentials')

        return {
            'email': user.email,
            'refresh': user.refresh,
            'access': user.access,
        }

class CreateUsernameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['username', 'user']