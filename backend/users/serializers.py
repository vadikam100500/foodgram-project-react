from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction
from rest_framework import serializers

from interactions.models import Follow

User = get_user_model()


class CustomUserGetSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj.id).exists()


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'username',
            'first_name', 'last_name',
            'password'
        )

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")
        if password:
            try:
                validate_password(password, user)
            except django_exceptions.ValidationError as e:
                serializer_error = serializers.as_serializer_error(e)
                raise serializers.ValidationError(
                    {"password": serializer_error["non_field_errors"]}
                )
        return attrs

    def create(self, validated_data):
        try:
            return self.perform_create(validated_data)
        except IntegrityError:
            self.fail("Не удалось создать пользователя")

    def perform_create(self, validated_data):
        with transaction.atomic():
            return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.password = make_password(
            validated_data.get('password', instance.password)
        )
        instance.save()
        return instance
