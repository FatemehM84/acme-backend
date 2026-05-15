from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
# from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()

#--register mode-----------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'password',
            'password2',
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match"}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')

        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )

        return user
    


#--login mode--------------------------------------
class LoginSerializer(serializers.Serializer):

    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        identifier = attrs.get('identifier')
        password = attrs.get('password')
        user = User.objects.filter(email=identifier).first()

        if not user:
            user = User.objects.filter(username=identifier).first()

        if user and user.check_password(password):

            refresh = RefreshToken.for_user(user)

            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                }
            }

        raise serializers.ValidationError(
            "Invalid credentials"
        )
    
#--logout------------------------------------------
class LogoutSerializer(serializers.Serializer):
    
    refresh = serializers.CharField()
    def save(self):
        token = RefreshToken(self.validated_data['refresh'])
        token.blacklist()

#--meview------------------------------------------
class MeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    username = serializers.CharField()

