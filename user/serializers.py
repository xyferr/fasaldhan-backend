from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, FarmerProfile, BuyerProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'user_type', 
                 'phone_number', 'location', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def validate_user_type(self, value):
        if value not in ['farmer', 'buyer']:
            raise serializers.ValidationError("User type must be either 'farmer' or 'buyer'")
        return value

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile (basic info)
    """
    has_profile = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'user_type', 'phone_number', 'location', 'is_verified', 
                 'has_profile', 'date_joined')
        read_only_fields = ('id', 'username', 'is_verified', 'date_joined')


class FarmerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for farmer profile
    """
    completion_percentage = serializers.ReadOnlyField()
    user_info = UserProfileSerializer(source='user', read_only=True)

    class Meta:
        model = FarmerProfile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class BuyerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for buyer profile
    """
    completion_percentage = serializers.ReadOnlyField()
    user_info = UserProfileSerializer(source='user', read_only=True)

    class Meta:
        model = BuyerProfile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)