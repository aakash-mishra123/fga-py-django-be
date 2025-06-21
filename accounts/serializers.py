from rest_framework import serializers
from accounts.models import  Otp, Address,UserCardDeatils, User,State,Cities,GustUser,PrimeMemberPlan, PlanBenefits,CountryCode,UserSubscription
import math, random
from datetime import datetime

from accounts.utils import Util
from django.core.cache import cache
from accounts.cache_utils import cache_with_prefix, invalidate_cache_pattern, invalidate_prefix
import os
import environ
env = environ.Env()
environ.Env.read_env()
import logging
logger = logging.getLogger(__name__)

def generateOTP() :
    digits = "0123456789"
    OTP = ""
    for i in range(6) :
        OTP += digits[math.floor(random.random() * 10)]

    return OTP

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'mobile','fcm_token','country_code','status','deleted_at']
        extra_kwargs={
            'password' : {'write_only': True}
        }
        depth = 1
        status = 1

    def validate(self, attrs):
        if not attrs['mobile']:
          raise serializers.ValidationError({'error':'Email should not be empty !'})
        return attrs

    def create(self, validated_data):
        # create user
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data,status=0)
        user.set_password(password)
        user.save()
        return user

class GustUserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','device_id']

class GustUUserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','device_id']

    def validate(self, attrs):
        if not attrs['device_id']:
          raise serializers.ValidationError({'error':'device_id should not be empty !'})
        return attrs

    def create(self, validated_data):
        # create user
        guestuser = GustUser.objects.create(**validated_data)
        guestuser.save()
        return guestuser

class UserLoginSerializer(serializers.ModelSerializer):
  mobile = serializers.CharField(max_length=255)
  class Meta:
    model = User
    fields = ['mobile', 'password']

class UserGuestSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id','device_id']


class UserSocialRegistrationSerializer(serializers.ModelSerializer):
  class Meta:
        model = User
        fields = ['email', 'mobile', 'provider', 'full_name', 'provider_id']
        depth = 1

  def create(self, validated_data):
        # Set 'mobile' to the current date formatted as Date_YYYYMMDD
        validated_data['mobile'] = 'Date_' + datetime.now().strftime('%Y%m%d%H%M%S')[-2:]


        # Create the user with the modified data
        user = User.objects.create(**validated_data)
        return user

class UserSocialSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(max_length=255)
  class Meta:
    model = User
    fields = ['id','email', 'mobile', 'full_name', 'provider_id']

class UserLoginOtpSerializer(serializers.ModelSerializer):
  mobile = serializers.CharField(max_length=255)
  class Meta:
    model = User
    fields = [ 'mobile']

class UserCarddetailsSerializer(serializers.ModelSerializer):
   class Meta:
    model = UserCardDeatils
    fields ='__all__'



class UserProfileSerializer(serializers.ModelSerializer):
  mobile = serializers.SerializerMethodField()

  def get_mobile(self, user):
        # Check if the mobile number is None, return an empty string if True
      return str(user.mobile) if user.mobile is not None and str(user.mobile) != "None" else ""


  class Meta:
    model = User
    fields = ['id', 'email', 'full_name' ,'profile_image','mobile']

class SendPasswordResetEmailSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=255)
    class Meta:
      fields = ['mobile']

    def validate(self, attr):
      mobile = attr.get('mobile')
      if User.objects.filter(mobile=mobile).exists():
        user = User.objects.get(mobile = mobile)
        otp = generateOTP()
        Otp.objects.create(
           type='forgot password',
           otp = 12345,
           user=user)
        # body = 'Forgot password OTP '+otp
        # # Send EMail
        # data = {
        #   'subject':'Reset Your Password',
        #   'body':body,
        #   'to_email':user.email
        # }
        # Util.send_email(data)
        return user
      else:
        raise serializers.ValidationError('You are not a Registered User')


class SendLoginOtpSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=255)
    class Meta:
      fields = ['mobile']

    def validate(self, attr):
      mobile = attr.get('mobile')
      if User.objects.filter(mobile=mobile).exists():
        user = User.objects.get(mobile = mobile)
        otp = generateOTP()
        Otp.objects.create(
           type='login otp',
           otp = 12345,
           user=user)
        # body = 'Forgot password OTP '+otp
        # # Send EMail
        # data = {
        #   'subject':'Reset Your Password',
        #   'body':body,
        #   'to_email':user.email
        # }
        # Util.send_email(data)

        return user
      else:
        raise serializers.ValidationError('You are not a Registered User')

class VerifyOtpSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=255)
    otp = serializers.CharField(max_length=255)

    class Meta:
      fields = ['mobile', 'otp']

    def validate(self, attr):
      mobile = attr.get('mobile')
      otp = attr.get('otp')
      if User.objects.filter(mobile = int(mobile)).exists():
        user = User.objects.get(mobile = int(mobile))
        userOtp = Otp.objects.filter(user_id = user.id, type="forgot password").last()

        print(userOtp)
        if int(userOtp.otp) == int(otp):
          return attr
        else:
          raise serializers.ValidationError('Invalid Otp')
      else:
        raise serializers.ValidationError('You are not a Registered User')

class LoginWithOtpSerializer(serializers.Serializer):
   mobile = serializers.CharField(max_length=255)
   otp = serializers.CharField(max_length=255)
   class Meta:
      fields = ['mobile', 'otp']

   def validate(self, attr):
      mobile = attr.get('mobile')
      otp = attr.get('otp')
      if User.objects.filter(mobile = int(mobile)).exists():
        user = User.objects.get(mobile = int(mobile))
        userOtp = Otp.objects.filter(user_id = user.id).last()
        if int(userOtp.otp) == int(otp):
          return attr
        else:
          raise serializers.ValidationError('Invalid Otp')
      else:
        raise serializers.ValidationError('You are not a Registered User')

class UserPasswordResetSerializer(serializers.Serializer):
  password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  confirm_password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  mobile = serializers.CharField(max_length=255)

  class Meta:
    fields = ['mobile','password', 'confirm_password']

  def validate(self, attrs):
    password = attrs.get('password')
    confirm_password = attrs.get('confirm_password')
    mobile = attrs.get('mobile')
    if password != confirm_password:
      raise serializers.ValidationError("Password and Confirm Password doesn't match")
    user = User.objects.get(mobile=mobile)
    user.set_password(password)
    user.save()
    return attrs



class ChangePasswordSerializer(serializers.Serializer):

    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        # Get passwords from environment variables with fallbacks
        new_password = env('DEFAULT_NEW_PASSWORD', default=data.get('new_password'))
        confirm_password = env('DEFAULT_CONFIRM_PASSWORD', default=data.get('confirm_password'))
        
        if new_password != confirm_password:
            raise serializers.ValidationError("New password and confirm password must match.")
            
        return data

class UserFullProfileSerializer(serializers.ModelSerializer):
  address = serializers.SerializerMethodField()
  prime = serializers.SerializerMethodField()

  def get_address(self, user):
      # Try to get from cache first
      cache_key = f"user_{user.id}_default_address"
      address_data = cache.get(cache_key)
      
      if address_data is None:
          qs = Address.objects.filter(deafult=1, user=user)
          serializer = GetAddressSerializer(instance=qs, many=True)
          if serializer.data:
              address_data = serializer.data[0]
              # Cache default address for quick retrieval
              cache.set(cache_key, address_data, timeout=300)
          else:
              address_data = {}
      
      return address_data

  def get_prime(self, user):
        # Try to get from cache first
        cache_key = f"user_{user.id}_prime_status"
        prime_status = cache.get(cache_key)
        
        if prime_status is None:
            prime_status = UserSubscription.objects.filter(user=user, status=1, payment_status=9).exists()
            # Cache prime status for quick retrieval
            cache.set(cache_key, prime_status, timeout=300)
        
        return prime_status


  class Meta:

    model = User
    fields = ['id','email', 'full_name', 'mobile','country_code', 'birth_date', 'profile_image','address','prime' ,'provider']
    depth = 1

class UpdateProfileSerializer(serializers.ModelSerializer):
  country_code = serializers.IntegerField(required=False)
  class Meta:
        model = User
        fields = ['id','email', 'full_name', 'mobile', 'birth_date', 'profile_image','country_code']
        depth = 1
  birth_date = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d', 'iso-8601'])

class UpdateProfileimgSerializer(serializers.ModelSerializer):
  country_code = serializers.IntegerField(required=False)
  class Meta:
        model = User
        fields = ['id','email', 'full_name', 'mobile', 'birth_date','country_code']
        depth = 1

class UpdateProfileImageSerializer(serializers.ModelSerializer):
  class Meta:
        model = User
        fields = ['id','profile_image']
        depth = 1

class GetStateSerializer(serializers.ModelSerializer):
   class Meta:
      model = State
      fields = ['id', 'state_name', 'country_name', 'state_code']

class GetCitiesSerializer(serializers.ModelSerializer):
   class Meta:
      model = Cities
      fields = ['id', 'city_name', 'state_name', 'state_code']

class AddAddressSerializer(serializers.ModelSerializer):
  class Meta:
    model = Address

    fields = ['id','house_no','bulding_name','street_address','state','contact_number', 'city', 'latitude', 'longitude','pincode','deafult','address','address_info']



  def create(self, validated_data):
        user = self.context['request'].user
        address = Address.objects.create(**validated_data, user=user)
        
        # Invalidate user's address caches
        try:
            invalidate_prefix(f"user_{user.id}_addresses")
            invalidate_cache_pattern(f"user_profile_{user.id}")
            logger.debug(f"Invalidated address cache after create for user {user.id}")
        except Exception as e:
            logger.error(f"Error invalidating address cache: {str(e)}")
            
        return address

class GetAddressSerializer(serializers.ModelSerializer):
  class Meta:
    model = Address
    fields = fields = ['id','house_no','bulding_name','street_address','state','contact_number', 'city', 'latitude', 'longitude','pincode','deafult','address','address_info']
    depth = 1

class UpdateAddressSerializer(serializers.ModelSerializer):
  class Meta:
    model = Address

    fields = fields = ['id','house_no','bulding_name','street_address','state', 'city', 'latitude', 'longitude','pincode','deafult','address','address_info']




class PrimePlanSerializer(serializers.ModelSerializer):
  class Meta:
    model = PrimeMemberPlan
    fields = '__all__'

class PlanBenefitsSerializer(serializers.ModelSerializer):
  class Meta:
    model = PlanBenefits
    fields = '__all__'

class CountryCodeSerializer(serializers.ModelSerializer):
  class Meta:
    model = CountryCode
    fields = '__all__'

class UserSubscriptionSerializer(serializers.ModelSerializer):
  class Meta:
    model = UserSubscription
    fields = ['id','order_id','plan_amount','plan_expiredate','status','plan_id', 'user_id']

class MonthlyUserCountSerializer(serializers.Serializer):
    class Meta:
      month = serializers.CharField()  # Field for the month name
      count = serializers.IntegerField()
