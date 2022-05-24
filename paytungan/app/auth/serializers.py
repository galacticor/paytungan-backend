from rest_framework import serializers


class GetUserRequest(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)


class GetByUsernameRequest(serializers.Serializer):
    username = serializers.CharField()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    firebase_uid = serializers.CharField()
    phone_number = serializers.CharField()
    username = serializers.CharField(
        required=False, default=None, allow_null=True, allow_blank=True
    )
    email = serializers.EmailField(
        required=False, default=None, allow_null=True, allow_blank=True
    )
    name = serializers.CharField(
        required=False, default=None, allow_null=True, allow_blank=True
    )
    profil_image = serializers.CharField(
        required=False, default=None, allow_null=True, allow_blank=True
    )
    is_onboarding = serializers.BooleanField(default=False)


class GetUserResponse(serializers.Serializer):
    data = UserSerializer()


class CreateUserRequest(serializers.Serializer):
    firebase_uid = serializers.CharField()
    phone_number = serializers.CharField()
    username = serializers.CharField(
        required=False, default=None, allow_null=True, allow_blank=True
    )
    email = serializers.EmailField(
        required=False, default=None, allow_null=True, allow_blank=True
    )
    name = serializers.CharField(
        required=False, default=None, allow_null=True, allow_blank=True
    )
    profil_image = serializers.CharField(
        required=False, default=None, allow_null=True, allow_blank=True
    )
    is_onboarding = serializers.BooleanField(default=False)


class CreateUserResponse(serializers.Serializer):
    data = UserSerializer()


class LoginRequest(serializers.Serializer):
    token = serializers.CharField()


class LoginResponse(serializers.Serializer):
    data = UserSerializer()


class UpdateUserRequest(serializers.Serializer):
    username = serializers.CharField()
    name = serializers.CharField()
    email = serializers.EmailField()
    profil_image = serializers.CharField(
        required=False, default=None, allow_null=True, allow_blank=True
    )


class UpdateUserResponse(serializers.Serializer):
    data = UserSerializer()
