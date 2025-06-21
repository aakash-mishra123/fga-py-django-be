from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from accounts.serializers import UserRegistrationSerializer,UserCarddetailsSerializer,UpdateProfileImageSerializer,UpdateProfileimgSerializer,UserSubscriptionSerializer,CountryCodeSerializer,PlanBenefitsSerializer,PrimePlanSerializer,GustUserRegistrationSerializer,GustUUserRegistrationSerializer,UserLoginOtpSerializer,UserLoginSerializer,UserGuestSerializer,GetCitiesSerializer,GetStateSerializer,SendLoginOtpSerializer,LoginWithOtpSerializer, UserLoginSerializer,UserProfileSerializer, SendPasswordResetEmailSerializer, VerifyOtpSerializer, UserPasswordResetSerializer, UserFullProfileSerializer, UpdateProfileSerializer, AddAddressSerializer, GetAddressSerializer, UpdateAddressSerializer,UserSocialSerializer, UserSocialRegistrationSerializer
from rest_framework.generics import GenericAPIView, UpdateAPIView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from accounts.models import Address,DeviceVersion, User,UserCardDeatils,Otp, LoginOtp,State,Cities,Cart,PrimeMemberPlan, PlanBenefits,CountryCode,UserSubscription,FcmToken
from banner.models import Notification
from django.urls import reverse
from django.contrib.auth.forms import  PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.forms import  CustomPasswordChangeForm
from rest_framework import status
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import HttpResponseForbidden
from rest_framework import permissions
import requests

from .serializers import ChangePasswordSerializer
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from django.db.models import Count
from django.db.models.functions import ExtractMonth,ExtractYear
from product.models import Order,ApplyCoupon
from django.db.models import Sum, Q, F, IntegerField, ExpressionWrapper, Value
from django.db.models.functions import Cast, Coalesce
from django.shortcuts import render
import calendar
from order.serializers import AddTipSerializer,OrderDetailSerializer
from datetime import datetime
from datetime import date
import random
import calendar
from django.http import HttpRequest
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import render
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .firebase_service import FirebaseMessaging
import firebase_admin
from firebase_admin import credentials, messaging, initialize_app, get_app
from accounts.cache_utils import cache_result, invalidate_prefix, invalidate_cache_pattern
from django.core.cache import cache

import logging
logger = logging.getLogger(__name__)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class AppVerion(GenericAPIView):

    def post(self, request, format=None):
        device_version = request.data.get('device_version')
        get_version = DeviceVersion.objects.first()

        try:
            device_version_float = float(device_version)
            current_version_float = float(get_version.version)
            min_version_float = float(get_version.min)

            if device_version_float < min_version_float:
                return Response({'status': True, 'msg': "Forced Update"}, status=status.HTTP_200_OK)
            elif min_version_float <= device_version_float < current_version_float:
                return Response({'status': True, 'msg': "optional"}, status=status.HTTP_200_OK)
            else:
                return Response({'status': True, 'msg': ""}, status=status.HTTP_200_OK)

        except ValueError:
            return Response({'status': False, 'data': {}, 'msg': "Invalid float values"}, status=status.HTTP_200_OK)


class UserRegistrationView(GenericAPIView):
    serializer_class = UserRegistrationSerializer
    def post(self, request, format= None):
        serializer = UserRegistrationSerializer(data= request.data)
        chk_deleteaccount = User.objects.filter(mobile=request.data.get('mobile'), deleted_at=None).last()
        if chk_deleteaccount is not None:
            chkuser = User.objects.filter(mobile = request.data.get('mobile'),status = 0).first()
            if chkuser:
                mobile = request.data.get('mobile')
                country_code = request.data.get('country_code')
                auth_key = "403949AMfDHjji64e4928cP1"
                template_id = "64e491ced6fc056a7669fab2"
                country =  country_code
                mobile_number = f"{country_code}{mobile}"
                otp = random.randint(1000,9999)
                Otp.objects.create(
                type='register otp',
                otp = otp,
                status = 0,
                mobile=mobile)

                url = f"https://control.msg91.com/api/v5/otp?template_id={template_id}&mobile={mobile_number}&otp={otp}"

                headers = {
                        'accept': 'application/json',
                        'content-type': 'application/json',
                        'authkey': auth_key,
                        'Cookie': 'PHPSESSID=mt56d5k6q49n1v9fpcr0qphb26'
                        }

                        # response = requests.request("POST", url, headers=headers, data=payload)

                response = requests.get( url, headers=headers)
                response_data = response.json()
                message = response_data.get("message")
                if response.status_code == 200:
                    # Invalidate any existing cache for this mobile number
                    invalidate_cache_pattern(f"user_mobile_{mobile}")
                    return Response({'status': True, 'data': {}, 'msg': "OTP sent successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({'status': False, 'data': {}, 'msg': "OTP not sent"}, status=status.HTTP_200_OK)
            else:

                if not serializer.is_valid():
                    default_errors = serializer.errors
                    new_error = {}
                    for field_name, field_errors in default_errors.items():
                        new_error[field_name] = field_errors[0]
                        break
                    return Response({'status':False, 'data':{}, 'msg':list(new_error.values())[0]})
                mobile = request.data.get('mobile')
                country_code = request.data.get('country_code')
                auth_key = "403949AMfDHjji64e4928cP1"
                template_id = "64e491ced6fc056a7669fab2"
                country =  country_code
                mobile_number = f"{country_code}{mobile}"
                otp = random.randint(1000,9999)
                Otp.objects.create(
                type='register otp',
                otp = otp,
                status = 0,
                mobile=mobile)

                url = f"https://control.msg91.com/api/v5/otp?template_id={template_id}&mobile={mobile_number}&otp={otp}"

                headers = {
                        'accept': 'application/json',
                        'content-type': 'application/json',
                        'authkey': auth_key,
                        'Cookie': 'PHPSESSID=mt56d5k6q49n1v9fpcr0qphb26'
                        }

                        # response = requests.request("POST", url, headers=headers, data=payload)

                response = requests.get( url, headers=headers)
                response_data = response.json()
                message = response_data.get("message")
                instance = serializer.save()
                token = get_tokens_for_user(instance)
                userregister_details = serializer.data
                userregister_details['token'] = token
                # Invalidate any potential cache for this mobile number
                invalidate_cache_pattern(f"user_mobile_{mobile}")
                if response.status_code == 200:

                    return Response({'status': True, 'data': {}, 'msg': "OTP sent successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({'status': False, 'data': {}, 'msg': "OTP not sent"}, status=status.HTTP_200_OK)
        else:
                upmobileno = request.data.get('mobile')
                emailup = request.data.get('email')
                random_number = random.randint(1000, 9999)
                upmobileno_with_random = f'{upmobileno}{random_number}'
                upemailno_with_random = f'{emailup}{random_number}'
                # updatemobile = User.objects.filter(mobile = request.data.get('mobile')).update(mobile = upmobileno_with_random,email=upemailno_with_random,old_mobile = upmobileno,old_email = emailup, country_code =country_code)
                fullname = request.data.get('full_name')
                fcm_token = request.data.get('fcm_token')
                password = request.data.get('password')
                email = request.data.get('email')
                mobile = request.data.get('mobile')
                country_code = request.data.get('country_code')
                auth_key = "403949AMfDHjji64e4928cP1"
                template_id = "64e491ced6fc056a7669fab2"
                updatemobile = User.objects.filter(mobile = request.data.get('mobile')).update(mobile = upmobileno_with_random,email=upemailno_with_random,old_mobile = upmobileno,old_email = emailup, country_code =country_code)
                country =  country_code
                mobile_number = f"{country_code}{mobile}"
                otp = random.randint(1000,9999)
                Otp.objects.create(
                type='register otp',
                otp = otp,
                status = 0,
                mobile=mobile)

                url = f"https://control.msg91.com/api/v5/otp?template_id={template_id}&mobile={mobile_number}&otp={otp}"

                headers = {
                        'accept': 'application/json',
                        'content-type': 'application/json',
                        'authkey': auth_key,
                        'Cookie': 'PHPSESSID=mt56d5k6q49n1v9fpcr0qphb26'
                        }

                        # response = requests.request("POST", url, headers=headers, data=payload)

                adduser = User(fcm_token=fcm_token,password=password,email=email,mobile=mobile, country_code=country_code,full_name=fullname,status =0)
                adduser.set_password(password)
                adduser.save()

                # Invalidate any cache related to this mobile or email
                invalidate_cache_pattern(f"user_mobile_{mobile}")
                invalidate_cache_pattern(f"user_email_{email}")
                
                response = requests.get( url, headers=headers)
                response_data = response.json()
                message = response_data.get("message")
                if response.status_code == 200:

                    return Response({'status': True, 'data': {}, 'msg': "OTP sent successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({'status': False, 'data': {}, 'msg': "OTP not sent"}, status=status.HTTP_200_OK)


def is_chkusers(user):
    name = ['deliveryboy','fulfillmentmanager','storemanager','storeboy']
    return user.groups.filter(name__in=name).exists()

# class UserRegistrationView(GenericAPIView):
#     serializer_class = UserRegistrationSerializer
#     def post(self, request, format= None):
#         serializer = UserRegistrationSerializer(data= request.data)

#         if not serializer.is_valid():
#             default_errors = serializer.errors
#             new_error = {}
#             for field_name, field_errors in default_errors.items():
#                 new_error[field_name] = field_errors[0]
#                 break
#             return Response({'status':False, 'data':{}, 'msg':list(new_error.values())[0]})

#         instance = serializer.save()
#         token = get_tokens_for_user(instance)
#         userregister_details = serializer.data
#         userregister_details['token'] = token
#         return Response({'status':True, 'data':userregister_details, 'msg':'user register successfully'})

class UserLoginView(GenericAPIView):
    serializer_class = UserLoginSerializer

    @cache_result(timeout=60, key_prefix="user_login_attempt")
    def get_user_login_attempts(self, mobile):
        """Cache login attempts to prevent brute force attacks"""
        return User.objects.filter(mobile=mobile, deleted_at=None).count()

    def post(self, request, format=None):
        try:
            serializer = UserLoginSerializer(data= request.data)
            serializer.is_valid(raise_exception=True)
            mobile = serializer.data.get('mobile')
            password = serializer.data.get('password')

            # Use cached method to check user existence (prevents brute force attempts)
            user_exists = self.get_user_login_attempts(mobile) > 0
            if not user_exists:
                return Response({'status':False, 'data':{}, 'msg':'Mobile no. or password is wrong'}, status=status.HTTP_200_OK)

            user = authenticate(mobile=mobile, password=password,deleted_at=None)

            if user and user.deleted_at is None:
                deliverboy = not is_chkusers(user)
                if deliverboy:
                    token = get_tokens_for_user(user)
                    login(request, user)
                    userData = UserProfileSerializer(request.user)
                    userProfie =  userData.data
                    userProfie['token']= token
                    user_id =   userProfie['id']
                    
                    # Invalidate all user-related caches for this user
                    invalidate_prefix(f"user_{user_id}")
                    invalidate_prefix(f"user_profile:{user_id}")
                    invalidate_cache_pattern(f"user_mobile_{mobile}")
                    
                    if User.objects.filter(device_id = request.data.get('device_id')).exists():
                        get_id = User.objects.filter(device_id = request.data.get('device_id')).first()
                        update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)
                        # Invalidate address caches when transferring addresses
                        invalidate_prefix(f"user_address:{get_id.id}")
                        invalidate_prefix(f"user_address:{user_id}")

                    chkdevice_id = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).first()
                    if chkdevice_id:
                            updatetoken = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).update(fcm_token = request.data.get('fcm_token'))
                    else:
                            user_id =   userProfie['id']

                            fcm = request.data.get('fcm_token')
                            device_id = request.data.get('device_id')
                            updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
                            updatetoken.save()
                    # update_fcm_token = User.objects.filter(mobile=mobile).update(fcm_token = request.data.get('fcm_token'))
                    return Response({'status':True, 'data': userProfie, 'msg':'Logged in successfully!'}, status=status.HTTP_200_OK)
                else:
                    return Response({'status':False, 'data': {}, 'msg' : 'User Id is not registered for this customer'}, status=status.HTTP_200_OK)
            else:
                return Response({'status':False, 'data':{}, 'msg':'Mobile no. or password is wrong'}, status=status.HTTP_200_OK)
        except:
                return Response({'status':False, 'data':{}, 'msg':'Mobile no. or password is wrong'}, status=status.HTTP_200_OK)

class GuestUserView(GenericAPIView):
    serializer_class = UserGuestSerializer

    @cache_result(timeout=300, key_prefix="guest_user")
    def get_guest_user(self, device_id):
        """Cache guest user data to reduce database queries"""
        return User.objects.filter(device_id=device_id).first()

    def post(self, request, format=None):
        serializer = UserGuestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device_id = serializer.data.get('device_id')
        
        # Use cached version if available
        user = self.get_guest_user(device_id)

        if user is not None:
            token = get_tokens_for_user(user)
            userregister_details = UserGuestSerializer(user).data
            userregister_details['token'] = token
            updatetoken_user = User.objects.filter(device_id=device_id).update(access_token=token.get('access'))
            #updatetoken = GustUser.objects.filter(device_id=device_id).update(access_token=token.get('access'))

            return Response({'status': True, 'data': userregister_details, 'msg': 'Login Successful'}, status=status.HTTP_200_OK)
        else:
            timestamp = str(int(datetime.timestamp(datetime.now())))
            email = f"mel@-{timestamp}"
            mobile = timestamp
            serializer = GustUserRegistrationSerializer(data=request.data)

            if not serializer.is_valid():
                default_errors = serializer.errors
                new_error = {}
                for field_name, field_errors in default_errors.items():
                    new_error[field_name] = field_errors[0]
                    break
                return Response({'status': False, 'data': {}, 'msg': list(new_error.values())[0]})
            
            usersave = User(device_id=device_id, email=email, mobile=mobile)
            usersave.save()  # Save the user object

            token = get_tokens_for_user(usersave)
            userregister_details = serializer.data
            userregister_details['token'] = token

            updatetoken_user = User.objects.filter(device_id=device_id).update(access_token=token.get('access'))
            
            # Invalidate guest user cache for this device_id
            invalidate_prefix(f"guest_user:{device_id}")

            return Response({'status': True, 'data': userregister_details, 'msg': 'Data saved successfully'})

class MergeTokenView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        user_id = request.user.id
        guest_token = request.data.get('guest_token')
        login_token = request.data.get('login_token')
        device_id = request.data.get('device_id')
        chk_token = User.objects.filter(device_id = device_id,access_token = login_token).first()

        if chk_token:
           return Response({'status':False, 'data':{}, 'msg':'Login token is worng please check login token'})
        else:
         logintoken = {}
         logintoken['access_token'] = login_token
         get_guest_id = User.objects.filter(device_id = device_id,access_token = guest_token).first()        

         if get_guest_id:
             guest_user_id = get_guest_id.id
             
             # Update cart user ID
             update_cart_user_id = Cart.objects.filter(user_id = guest_user_id).update(user_id = user_id)
             
             # Invalidate relevant caches after merging user data
             invalidate_prefix(f"user_{guest_user_id}")
             invalidate_prefix(f"user_{user_id}")
             invalidate_prefix(f"guest_user:{device_id}")
             invalidate_prefix(f"user_cart:{guest_user_id}")
             invalidate_prefix(f"user_cart:{user_id}")
             
             return Response({'status':True, 'data':logintoken, 'msg':'Token merge use this token'})
         else:
             return Response({'status':False, 'data':{}, 'msg':'Guest token not found'})
         
# class UserSocialLoginView(GenericAPIView):
#     def post(self, request, format=None):
#         if not User.objects.filter(provider_id=request.data['provider_id']).exists():
#             serializer = UserSocialRegistrationSerializer(data= request.data)
#             if not serializer.is_valid():
#              default_errors = serializer.errors
#              new_error = {}
#              for field_name, field_errors in default_errors.items():
#                 new_error[field_name] = field_errors[0]
#                 break
#              return Response({'status':False, 'data':{}, 'msg':list(new_error.values())[0]})
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             email = serializer.data.get('email')
#             provider_id = serializer.data.get('provider_id')
#             user = User.objects.filter(email=email,provider_id=provider_id).get()
#             token = get_tokens_for_user(user)
#             login(request, user)
#             userData = UserProfileSerializer(request.user)
#             userProfie =  userData.data
#             userProfie['token']= token
#             return Response({'status':True, 'data': userProfie, 'msg':'Login Success'}, status=status.HTTP_200_OK)
#         else:
#             return Response({'status':False, 'data': {}, 'msg':'user already register please login'}, status=status.HTTP_200_OK)


        # serializer = UserSocialSerializer(data= request.data)
        # serializer.is_valid(raise_exception=True)
        # email = serializer.data.get('email')
        # provider_id = serializer.data.get('provider_id')
        # user = User.objects.filter(email=email,provider_id=provider_id).get()
        # token = get_tokens_for_user(user)
        # login(request, user)
        # userData = UserProfileSerializer(request.user)
        # userProfie =  userData.data
        # userProfie['token']= token
        # return Response({'status':True, 'data': userProfie, 'msg':'Login Success'}, status=status.HTTP_200_OK)


class UserSocialLoginView(GenericAPIView):
    def post(self, request, format=None):
     if request.data['provider'] == "facebook" :
           provider_id =  request.data['provider_id']
           email =  request.data['email']
           otp =  request.data['otp']
           if not User.objects.filter(provider_id=provider_id).exists():
                data = {}
                if otp == '1':
                    if User.objects.filter(email=email).exists():
                      return Response({'status':False, 'data': {}, 'msg':'This email already exists'}, status=status.HTTP_200_OK)
                    otp = random.randint(1000,9999)
                    email = request.data['email']
                    Otp.objects.create(
                        type='login otp',
                        otp = otp,
                        status = 0,
                        email=email)
                    data['otp'] = otp
                    subject = 'Melcom Login OTP'
                    message =  f"OTP is = {otp}"
                    from_email = 'online@melcomgroup.com'
                    recipient_list = [email]

                    send_mail(subject, message, from_email, recipient_list)
                elif otp == '0' and email:
                    if User.objects.filter(email=email).exists():
                      return Response({'status':False, 'data': {}, 'msg':'This email already exists'}, status=status.HTTP_200_OK)
                    serializer = UserSocialRegistrationSerializer(data= request.data)
                    if not serializer.is_valid():

                        default_errors = serializer.errors
                        new_error = {}
                        for field_name, field_errors in default_errors.items():
                            new_error[field_name] = field_errors[0]
                            break
                        return Response({'status':False, 'data':{}, 'msg':list(new_error.values())[0]})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    email = serializer.data.get('email')
                    provider_id = serializer.data.get('provider_id')
                    user = User.objects.filter(email=email).get()
                    token = get_tokens_for_user(user)
                    login(request, user)
                    userData = UserProfileSerializer(request.user)
                    userProfie =  userData.data
                    userProfie['token']= token
                    user_id =   userProfie['id']
                    # fcm = request.data.get('fcm_token')
                    # device_id = request.data.get('device_id')
                    # updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
                    # updatetoken.save()
                    if User.objects.filter(device_id = request.data.get('device_id')).exists():
                        get_id = User.objects.filter(device_id = request.data.get('device_id')).first()
                        update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)
                    chkdevice_id = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).first()
                    if chkdevice_id:
                            updatetoken = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).update(fcm_token = request.data.get('fcm_token'))
                    else:
                            user_id =   userProfie['id']
                            if User.objects.filter(device_id = request.data.get('device_id')).exists():
                                get_id = User.objects.filter(device_id = request.data.get('device_id')).first()
                                update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)

                            fcm = request.data.get('fcm_token')
                            device_id = request.data.get('device_id')
                            updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
                            updatetoken.save()
                    return Response({'status':True, 'data': userProfie, 'msg':'Login Successful'}, status=status.HTTP_200_OK)
                else:
                    data['otp'] = 0

                email =  request.data['email']
                token = {}
                token['refresh'] = None
                token['access'] = None

                data['id'] = None
                data['full_name'] = None
                data['mobile'] = None
                data['profile_image'] = None
                data['email'] = email
                data['token'] = token


                return Response({'status':True, 'data': data, 'msg':'Success'}, status=status.HTTP_200_OK)

           else:
                chk_email = User.objects.filter(provider_id=provider_id).first()
                if chk_email.email:

                    serializer = UserSocialSerializer(data= request.data)
                    provider_id = request.data.get('provider_id')
                    user = User.objects.filter(provider_id=provider_id).get()
                    token = get_tokens_for_user(user)
                    login(request, user)
                    userData = UserProfileSerializer(request.user)
                    userProfie =  userData.data
                    userProfie['token']= token
                    userProfie['otp']= 0
                    user_id =   userProfie['id']
                    fcm = request.data.get('fcm_token')
                    device_id = request.data.get('device_id')
                    # updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
                    # updatetoken.save()
                    if User.objects.filter(device_id = request.data.get('device_id')).exists():
                        get_id = User.objects.filter(device_id = request.data.get('device_id')).first()
                        update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)
                    chkdevice_id = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).first()
                    if chkdevice_id:
                            updatetoken = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).update(fcm_token = request.data.get('fcm_token'))
                    else:
                            user_id =   userProfie['id']

                            fcm = request.data.get('fcm_token')
                            device_id = request.data.get('device_id')
                            updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
                            updatetoken.save()
                            if User.objects.filter(device_id = request.data.get('device_id')).exists():
                                get_id = User.objects.filter(device_id = request.data.get('device_id')).first()
                                update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)
                    return Response({'status':True, 'data': userProfie, 'msg':'Login Successful'}, status=status.HTTP_200_OK)
                else:

                    token = {}
                token['refresh'] = None
                token['access'] = None
                data = {}
                data['id'] = None
                data['full_name'] = None
                data['mobile'] = None
                data['profile_image'] = None
                data['email'] = email
                data['otp'] = 0
                data['token'] = token
                return Response({'status':True, 'data': data, 'msg':'Success'}, status=status.HTTP_200_OK)

     if request.data['provider'] == "apple" :

         if not User.objects.filter(provider=request.data['provider'],provider_id = request.data['provider_id']).exists():

            serializer = UserSocialRegistrationSerializer(data= request.data)
            if not serializer.is_valid():

                default_errors = serializer.errors
                new_error = {}
                for field_name, field_errors in default_errors.items():
                    new_error[field_name] = field_errors[0]
                    break
                return Response({'status':False, 'data':{}, 'msg':list(new_error.values())[0]})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            email = serializer.data.get('email')
            provider_id = serializer.data.get('provider_id')
            user = User.objects.filter(email=email).get()
            token = get_tokens_for_user(user)
            login(request, user)
            userData = UserProfileSerializer(request.user)
            userProfie =  userData.data
            userProfie['token']= token
            user_id =   userProfie['id']
            fcm = request.data.get('fcm_token')
            device_id = request.data.get('device_id')
            # updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
            # updatetoken.save()
            if User.objects.filter(device_id = request.data.get('device_id')).exists():
                    get_id = User.objects.filter(device_id = request.data.get('device_id')).first()
                    update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)
            chkdevice_id = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).first()
            if chkdevice_id:
                            updatetoken = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).update(fcm_token = request.data.get('fcm_token'))
            else:
                            user_id =   userProfie['id']

                            fcm = request.data.get('fcm_token')
                            device_id = request.data.get('device_id')
                            updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
                            updatetoken.save()
                            if User.objects.filter(device_id = request.data.get('device_id')).exists():
                                get_id = User.objects.filter(device_id = request.data.get('device_id')).first()
                                update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)
            return Response({'status':True, 'data': userProfie, 'msg':'Login Successful'}, status=status.HTTP_200_OK)
         else:
            provider = request.data['provider']
            provider_id = request.data['provider_id']
            user = User.objects.filter(provider_id=provider_id).get()
            token = get_tokens_for_user(user)
            login(request, user)
            userData = UserProfileSerializer(request.user)
            userProfie =  userData.data
            userProfie['token']= token
            user_id =   userProfie['id']
            fcm = request.data.get('fcm_token')
            device_id = request.data.get('device_id')
            # updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
            # updatetoken.save()
            if User.objects.filter(device_id = request.data.get('device_id')).exists():
                    get_id = User.objects.filter(device_id = request.data.get('device_id')).first()
                    update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)
            chkdevice_id = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).first()
            if chkdevice_id:
                updatetoken = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).update(fcm_token = request.data.get('fcm_token'))
            else:
                    user_id =   userProfie['id']

                    fcm = request.data.get('fcm_token')
                    device_id = request.data.get('device_id')
                    updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
                    updatetoken.save()
                    if User.objects.filter(device_id = request.data.get('device_id')).exists():
                        get_id = User.objects.filter(device_id = request.data.get('device_id')).first()
                        update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)
            return Response({'status':True, 'data': userProfie, 'msg':'Login Successful'}, status=status.HTTP_200_OK)
     else:

        if not User.objects.filter(email=request.data['email']).exists():
            serializer = UserSocialRegistrationSerializer(data= request.data)

            if not serializer.is_valid():
             default_errors = serializer.errors
             new_error = {}
             for field_name, field_errors in default_errors.items():
                new_error[field_name] = field_errors[0]
                break
             return Response({'status':False, 'data':{}, 'msg':list(new_error.values())[0]})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            email = serializer.data.get('email')
            provider_id = serializer.data.get('provider_id')
            user = User.objects.filter(email=email).get()
            token = get_tokens_for_user(user)
            login(request, user)
            userData = UserProfileSerializer(request.user)
            userProfie =  userData.data
            userProfie['token']= token
            user_id =   userProfie['id']
            fcm = request.data.get('fcm_token')
            device_id = request.data.get('device_id')
            # updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
            # updatetoken.save()
            if User.objects.filter(device_id = request.data.get('device_id')).exists():
                    get_id = User.objects.filter(device_id = request.data.get('device_id')).first()
                    update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)
            chkdevice_id = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).first()
            if chkdevice_id:
                        updatetoken = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).update(fcm_token = request.data.get('fcm_token'))
            else:
                        user_id =   userProfie['id']

                        fcm = request.data.get('fcm_token')
                        device_id = request.data.get('device_id')
                        updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
                        updatetoken.save()
                        if User.objects.filter(device_id = request.data.get('device_id')).exists():
                            get_id = User.objects.filter(device_id = request.data.get('device_id')).first()
                            update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)
            return Response({'status':True, 'data': userProfie, 'msg':'Login Successful'}, status=status.HTTP_200_OK)
        else:

                serializer = UserSocialSerializer(data= request.data)
                serializer.is_valid(raise_exception=True)
                email = serializer.data.get('email')
                provider_id = serializer.data.get('provider_id')
                user = User.objects.filter(email=email).get()
                token = get_tokens_for_user(user)
                login(request, user)
                userData = UserProfileSerializer(request.user)
                userProfie =  userData.data
                userProfie['token']= token
                user_id =   userProfie['id']
                fcm = request.data.get('fcm_token')
                device_id = request.data.get('device_id')
                # updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
                # updatetoken.save()
                if User.objects.filter(device_id = request.data.get('device_id')).exists():
                        get_id = User.objects.filter(device_id = request.data.get('device_id')).first()
                        update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)
                chkdevice_id = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).first()
                if chkdevice_id:
                    updatetoken = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).update(fcm_token = request.data.get('fcm_token'))
                else:
                    user_id =   userProfie['id']

                    fcm = request.data.get('fcm_token')
                    device_id = request.data.get('device_id')
                    updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
                    updatetoken.save()
                    if User.objects.filter(device_id = request.data.get('device_id')).exists():
                        get_id = User.objects.filter(device_id = request.data.get('device_id')).first()
                        update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)
                return Response({'status':True, 'data': userProfie, 'msg':'Login Successful'}, status=status.HTTP_200_OK)

class UserSocialRegisView(GenericAPIView):
    def post(self, request, format=None):
        if User.objects.filter(provider_id=request.data['provider_id']).exists():
            provider_id = request.data['provider_id']
            user = User.objects.filter(provider_id=provider_id).get()
            token = get_tokens_for_user(user)
            login(request, user)
            userData = UserProfileSerializer(request.user)
            userProfie =  userData.data
            userProfie['token']= token
            user_id =   userProfie['id']
            fcm = request.data.get('fcm_token')
            device_id = request.data.get('device_id')
            # updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
            # updatetoken.save()
            if User.objects.filter(device_id = request.data.get('device_id')).exists():
                    get_id = User.objects.filter(device_id = request.data.get('device_id')).first()
                    update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)
            chkdevice_id = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).first()
            if chkdevice_id:
                updatetoken = FcmToken.objects.filter(device_id =  request.data.get('device_id'),user_id = user_id).update(fcm_token = request.data.get('fcm_token'))
            else:
                user_id =   userProfie['id']

                fcm = request.data.get('fcm_token')
                device_id = request.data.get('device_id')
                updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
                updatetoken.save()
                if User.objects.filter(device_id = request.data.get('device_id')).exists():
                    get_id = User.objects.filter(device_id = request.data.get('device_id')).first()
                    update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)
            return Response({'status':True, 'data': userProfie, 'msg':'Login Successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'status':False, 'data': {}, 'msg':'This user is not registered'}, status=status.HTTP_200_OK)

class SendPasswordResetEmailView(GenericAPIView):
    serializer_class = SendPasswordResetEmailSerializer
    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if not serializer.is_valid():
            default_errors = serializer.errors
            new_error = {}
            for field_name, field_errors in default_errors.items():
                new_error[field_name] = field_errors[0]
                break
            return Response({'status':False, 'data':{}, 'msg':list(new_error.values())[0]})

        return Response({'status':True,'msg':'OTP has been sent to your registered mobile number', 'data' : serializer.data}, status=status.HTTP_200_OK)

class VerifyOtpView(GenericAPIView):
    serializer_class = VerifyOtpSerializer
    def post(self, request, format=None):
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'status':True, 'data': {},"msg": 'Otp verify'}, status=status.HTTP_200_OK)

class RegisterOTPVerify(GenericAPIView):
   def post(self, request, format=None):

        otp = request.data.get('otp')
        mobile = request.data.get('mobile')
        userOtp = Otp.objects.filter(mobile = mobile,status = 0).last()
        if User.objects.filter(mobile=mobile).exists():
                user = User.objects.filter(mobile=mobile).first()
                if Otp.objects.filter(mobile = mobile,status = 0).exists():
                    userOtp = Otp.objects.filter(mobile = mobile,status = 0).last()
                    if int(userOtp.otp) == int(otp):
                        mobile_number =  {}
                        mobile_number['mobile_number'] = mobile
                        token = get_tokens_for_user(user)
                        login(request, user)
                        userData = UserProfileSerializer(request.user)
                        userProfie =  userData.data
                        userProfie['token']= token
                        userOtp = User.objects.filter(mobile = mobile,status = 0).update(status =1)

                        userOtp = Otp.objects.filter(mobile = mobile,status = 0).update(status =1)
                        user_id =   userProfie['id']
                        fcm = request.data.get('fcm_token')
                        device_id = request.data.get('device_id')
                        updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
                        updatetoken.save()
                        if User.objects.filter(device_id = device_id).exists():
                            get_id = User.objects.filter(device_id = device_id).first()
                            update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user.id)
                        return Response({'status':True, 'data': userProfie,"msg": 'OTP Verified'}, status=status.HTTP_200_OK)
                    else:
                     return Response({'status':False, 'data': {},"msg": 'Wrong Otp'}, status=status.HTTP_200_OK)
                else:
                    return Response({'status':False, 'data': {},"msg": 'Wrong Otp'}, status=status.HTTP_200_OK)

        else:
                return Response({'status': False, 'data': {}, 'msg': "This mobile number is not registered"}, status=status.HTTP_200_OK)

class UserAccountDelete(GenericAPIView):
   permission_classes = [IsAuthenticated]
   def get(self, request, format=None):
                user = request.user.id
                current_datetime = timezone.now()
                User.objects.filter(id =user).update(deleted_at = current_datetime)
                return Response({'status': True, 'data': {}, 'msg': "Your account deleted successfully"}, status=status.HTTP_200_OK)

class LoginVerifyOtp(GenericAPIView):
   def post(self, request, format=None):
        otp = request.data.get('otp')
        country_code = request.data.get('country_code')
        mobile = request.data.get('mobile')
        email=request.data.get('email')
        device_id=request.data.get('device_id')
        fcm_token=request.data.get('fcm_token')
        name=request.data.get('name')
        provider_id=request.data.get('provider_id')
        provider=request.data.get('provider')
        if email in [None, '']:
            if not otp:
                return Response({'error': 'OTP is required.'}, status=status.HTTP_200_OK)
            # Replace with the actual third-party API URL and API key
            if User.objects.filter(mobile=mobile).exists():
                user = User.objects.filter(mobile=mobile).first()
                if Otp.objects.filter(user_id = user.id,status = 0).exists():
                    userOtp = Otp.objects.filter(user_id = user.id,status = 0).last()
                    if int(userOtp.otp) == int(otp):
                        mobile_number =  {}
                        mobile_number['mobile_number'] = mobile
                        token = get_tokens_for_user(user)
                        login(request, user)
                        userData = UserProfileSerializer(request.user)
                        userProfie =  userData.data
                        userProfie['token']= token
                        device_id=request.data.get('device_id')

                        userOtp = Otp.objects.filter(user_id = user.id,status = 0).update(status =1)
                        if User.objects.filter(device_id = device_id).exists():
                            get_id = User.objects.filter(device_id = device_id).first()
                            update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user.id)
                        chkdevice_id = FcmToken.objects.filter(device_id =  request.data.get('device_id')).first()
                        if chkdevice_id:
                                user_id =   userProfie['id']
                                updatetoken = FcmToken.objects.filter(device_id =  request.data.get('device_id')).update(fcm_token = request.data.get('fcm_token'))                                
                                
                        else:
                            user_id =   userProfie['id']

                            fcm = request.data.get('fcm_token')
                            device_id = request.data.get('device_id')
                            updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
                            updatetoken.save()                            

                        return Response({'status':True, 'data': userProfie,"msg": 'OTP verified'}, status=status.HTTP_200_OK)
                    else:
                     return Response({'status':False, 'data': {},"msg": 'Wrong OTP'}, status=status.HTTP_200_OK)
                else:
                    return Response({'status':False, 'data': {},"msg": 'Wrong OTP'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': False, 'data': {}, 'msg': "This mobile number is not registered"}, status=status.HTTP_200_OK)
        else:
              if Otp.objects.filter(email = email,status = 0).exists():
                    userOtp = Otp.objects.filter(email = email,status = 0).last()
                    if int(userOtp.otp) == int(otp):
                        userOtp = Otp.objects.filter(email = email,status = 0).update(status =1)
                        serializer = UserSocialRegistrationSerializer(data= request.data)
                        if not serializer.is_valid():
                         default_errors = serializer.errors
                         new_error = {}
                         for field_name, field_errors in default_errors.items():
                            new_error[field_name] = field_errors[0]
                            break
                         return Response({'status':False, 'data':{}, 'msg':list(new_error.values())[0]})
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        email = serializer.data.get('email')
                        provider_id = serializer.data.get('provider_id')
                        user = User.objects.filter(email=email).get()
                        token = get_tokens_for_user(user)
                        login(request, user)
                        userData = UserProfileSerializer(request.user)
                        userProfie =  userData.data
                        userProfie['token']= token
                        user_id =   userProfie['id']
                        fcm = request.data.get('fcm_token')
                        device_id = request.data.get('device_id')
                        if User.objects.filter(device_id = device_id).exists():
                            get_id = User.objects.filter(device_id = device_id).first()
                            update_address = Address.objects.filter(user_id = get_id.id).update(user_id=user_id)
                        chkdevice_id = FcmToken.objects.filter(device_id =  request.data.get('device_id')).first()
                        if chkdevice_id:
                                updatetoken = FcmToken.objects.filter(device_id =  request.data.get('device_id')).update(fcm_token = request.data.get('fcm_token'))
                        else:

                            user_id =   userProfie['id']

                            fcm = request.data.get('fcm_token')
                            device_id = request.data.get('device_id')
                            updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
                            updatetoken.save()

                        return Response({'status':True, 'data': userProfie,"msg": 'OTP verified'}, status=status.HTTP_200_OK)
                    else:
                     return Response({'status':False, 'data': {},"msg": 'Wrong OTP'}, status=status.HTTP_200_OK)
              else:
                    return Response({'status':False, 'data': {},"msg": 'Wrong OTP'}, status=status.HTTP_200_OK)


class LoginWithOtp(GenericAPIView):
    serializer_class = SendLoginOtpSerializer
    def post(self, request, format=None):
        serializer = SendLoginOtpSerializer(data=request.data)
        if not serializer.is_valid():
            default_errors = serializer.errors
            new_error = {}
            for field_name, field_errors in default_errors.items():
                new_error[field_name] = field_errors[0]
                break
            return Response({'status':False, 'data':{}, 'msg':list(new_error.values())[0]})

        return Response({'status':True,'msg':'OTP has been sent, Please check.', 'data' : serializer.data}, status=status.HTTP_200_OK)

class TestMail(GenericAPIView):
    serializer_class = SendLoginOtpSerializer
    def post(self, request, format=None):
        otp = random.randint(1000,9999)
        email = 'singh.bhupendra@orangemantra.in'
        subject = 'Melcom Login OTP mail testing'
        message =  f"OTP is = {otp}"
        from_email = 'notifmail00@gmail.com'
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)

        return Response({'status':True,'msg':'OTP has been sent, Please check.', 'data' : 'Hello'}, status=status.HTTP_200_OK)


class UserPasswordResetView(GenericAPIView):
  serializer_class = UserPasswordResetSerializer
  def post(self, request, format=None):
    serializer = UserPasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'status':True, 'data': {}, 'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)

class UserProfileView(GenericAPIView):
  serializer_class = UserFullProfileSerializer
  permission_classes = [IsAuthenticated] #To check JWT Authentication inn POSTb Login API
  def get(self, request, format=None):

    serializer = UserFullProfileSerializer(request.user)
    print(serializer.data)

    return Response({'status':True, 'data': serializer.data, 'msg':'Success'}, status=status.HTTP_200_OK)


class UserUpdateProfileView(GenericAPIView):
    serializer_class = UpdateProfileSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        item = User.objects.get(pk=request.user.id)
        data = UpdateProfileSerializer(instance=item, data=request.data)
        if 'mobile' in request.data:
            # Normalize mobile number to remove the plus sign
            normalized_mobile = request.data['mobile'].lstrip('+')

            existing_user = User.objects.filter(
                Q(mobile=request.data['mobile']) | Q(mobile=normalized_mobile)
            ).exclude(id=request.user.id).first()

            if existing_user:
                return Response({
                    'status': False,
                    'data': {},
                    'msg': 'Mobile number already exists'
                }, status=status.HTTP_400_BAD_REQUEST)

        if data.is_valid():
            # Extract and update country code and mobile number
            country_code = data.validated_data.get('country_code', None)
            mobile = data.validated_data.get('mobile', None)

            if country_code is not None:
                request.user.country_code = country_code

            if mobile is not None:
                request.user.mobile = mobile

            data.save()

            return Response({
                'status': True,
                'data': data.data,
                'msg': 'Successfully Updated'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': False,
                'data': {},
                'msg': 'Profile is not updated yet'
            }, status=status.HTTP_200_OK)

class UserUpdateProfileViewWithIMG(GenericAPIView):
    serializer_class = UpdateProfileimgSerializer
    permission_classes = [IsAuthenticated]
    def put(self, request, format=None):
        item = User.objects.get(pk=request.user.id)
        data = UpdateProfileimgSerializer(instance=item, data=request.data)
        if data.is_valid():
            data.save()
            return Response({'status':True, 'data':data.data, 'msg': 'Successfully Updated'}, status=status.HTTP_200_OK)
        else:
            return Response({'status':False, 'data':{}, 'msg': 'Something went wrong'},status=status.HTTP_200_OK)

class UserUpdateProfileImageView(GenericAPIView):
    serializer_class = UpdateProfileImageSerializer
    permission_classes = [IsAuthenticated]
    def put(self, request, format=None):
        item = User.objects.get(pk=request.user.id)
        data = UpdateProfileImageSerializer(instance=item, data=request.data)
        if data.is_valid():
            data.save()
            return Response({'status':True, 'data':data.data, 'msg': 'Successfully Updated'}, status=status.HTTP_200_OK)
        else:
            return Response({'status':False, 'data':{}, 'msg': 'Something went wrong'},status=status.HTTP_200_OK)

class UserAddAddressView(GenericAPIView):
    serializer_class = AddAddressSerializer
    @cache_result(timeout=300, key_prefix="add_address")
    def post(self, request, format= None):
        serializer = AddAddressSerializer(data= request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({'status':False, 'data':serializer.errors, 'msg':'Something went wrong'})
        serializer.save()
        return Response({'status':True, 'data':serializer.data, 'msg':'Data saved successfully'})

class GetAddressView(GenericAPIView):
    serializer_class = GetAddressSerializer
    permission_classes = [IsAuthenticated]
    @cache_result(timeout=300, key_prefix="get_address")
    def get(self, request, format=None):
        query_set = Address.objects.filter(user_id=request.user.id)
        serializer = GetAddressSerializer(query_set, many=True)
        return Response({'status':True, 'data': serializer.data, 'msg': 'Success'}, status=status.HTTP_200_OK)

class StateList(GenericAPIView):
    serializer_class = GetStateSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        query_set = State.objects.all()
        serializer = GetStateSerializer(query_set, many=True)
        return Response({'status':True, 'data': serializer.data, 'msg': 'Success'}, status=status.HTTP_200_OK)

class CityList(GenericAPIView):
    serializer_class = GetCitiesSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        state_id = request.data.get('state_id')
        if state_id is None:
            return Response({'status': False, 'msg': 'Missing state id', 'data': None}, status=status.HTTP_200_OK)
        query_set = Cities.objects.filter(state_id = state_id)
        serializer = GetCitiesSerializer(query_set, many=True)
        return Response({'status':True, 'data': serializer.data, 'msg': 'Success'}, status=status.HTTP_200_OK)

class DeleteAddressView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, format=None):
        Address.objects.get(id = request.data.get('id')).delete()
        return Response({'status':True, 'data': {}, 'msg': 'Successfully deleted'}, status=status.HTTP_200_OK)

class UpdateAddressView(GenericAPIView):
    serializer_class = UpdateAddressSerializer
    permission_classes = [IsAuthenticated]
    def put(self, request, format=None):
        item = Address.objects.get(id=request.data.get('id'))
        data = UpdateAddressSerializer(instance=item, data=request.data)
        if data.is_valid():
            data.save()
            return Response({'status':True, 'data':data.data, 'msg': 'Successfully Updated'}, status=status.HTTP_200_OK)
        else:
            return Response({'status':False, 'data':{}, 'msg': 'Something went wrong'},status=status.HTTP_200_OK)
        
class SkipPrime(GenericAPIView):
    serializer_class = UpdateAddressSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        user_id = request.user.id
        update_skip = User.objects.filter(id = user_id).update(skip_prime=1)
        if(update_skip):       
            return Response({'status':True, 'data':{}, 'msg': 'Successfully Updated'}, status=status.HTTP_200_OK)
        else:
            return Response({'status':False, 'data':{}, 'msg': 'Something went wrong'},status=status.HTTP_200_OK)        

class UserLogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        device_id = request.data.get('device_id')
        user_id = request.user.id
        update_skip = User.objects.filter(id = user_id).update(skip_prime=0,is_store_popup=0)
        delete = FcmToken.objects.filter(device_id = device_id,user_id = request.user.id).delete()
        logout(request)
        return Response({'status':True, 'data': {},'msg': 'Logged Out Successfully!'}, status=status.HTTP_200_OK)

class CheckDays(GenericAPIView):
    @staticmethod
    def is_1st_or_3rd_wednesday(date):
        day_of_month = date.day
        week_of_month = (day_of_month - 1) // 7 + 1
        day_of_week = date.weekday()
        return (week_of_month == 1 and day_of_week == 2) or (week_of_month == 3 and day_of_week == 2)

    @staticmethod
    def get_1st_and_3rd_wednesday(queryset):
        return queryset.filter(is_1st_or_3rd_wednesday=True)

class CheckWednesday(GenericAPIView):
    def get(self, request, format=None):
        current_date = datetime.now().date()  # Get the current date
        is_special_day = CheckDays.is_1st_or_3rd_wednesday(current_date)

        # You can customize the response based on whether it's the 1st or 3rd Wednesday
        response_data = {
            'status': True,
            'is_special_day': is_special_day,
            'msg': 'Successfully checked for 1st or 3rd wednessday.'
        }

        return Response(response_data, status=status.HTTP_200_OK)

class MakeDefaultAddressView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        user = request.user
        id = request.data.get('id')
        if Address.objects.filter(id=id,deafult=1).exists():
            return Response({'status':False, 'data': {},'msg': 'Address Already Set As Default'})
        else:
            defaultAddress = Address.objects.get(id=id)
            defaultAddress.deafult = 1
            defaultAddress.save()
            Address.objects.exclude(id=id).filter(user=user).update(deafult=0)
            return Response({'status':True, 'data': {},'msg': 'Success'})

class UserProfileRemoveView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        user = request.user.id
        profileimg = None
        update_profile = User.objects.filter(id = user).update(profile_image = profileimg)
        return Response({'status':True, 'data': {},'msg': 'Success'})


class ChangePasswordView(GenericAPIView):
    # Specify the serializer class here
    serializer_class = ChangePasswordSerializer
    
    
    def get(self, request):
        # Use cache to store form to reduce processing overhead
        cache_key = f"password_form_{request.user.id}"
        def get_cached_or_set(key, func, timeout=None):
            val = cache.get(key)
            if val is None:
                val = func()
                cache.set(key, val, timeout)
            return val
        def get_form():
            return CustomPasswordChangeForm(request.user)
            
        form = get_cached_or_set(cache_key, get_form, timeout=60)
        return render(request, '../templates/admin/accounts/user/change_password.html', {'form': form})
    
    def post(self, request):
        import time
        start_time = time.time()
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Password change logic here
            
            # Invalidate relevant caches
            invalidate_prefix(f"user_profile_{request.user.id}")
            invalidate_cache_pattern(f"user_{request.user.id}")
            
            # Log performance
            execution_time = time.time() - start_time
            logger.info(f"Password changed for user {request.user.id} in {execution_time:.2f}s")
            
            return Response({
                "message": "Password changed successfully",
                "execution_time_ms": round(execution_time * 1000, 2)
            }, status=status.HTTP_200_OK)
        
        logger.warning(f"Invalid password change attempt for user {request.user.id}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestNotifications(GenericAPIView):
    # Initialize Firebase only once
    if not firebase_admin._apps.get("melcom-2a501"):
        cred = credentials.Certificate('melcom-2a501-59a077dbe1df.json')
        firebase_admin.initialize_app(cred, name="melcom-2a501")
    
    @cache_result(timeout=300, key_prefix="fcm_token")
    def get_user_fcm_token(self, manager_id):
        """Cached retrieval of user's FCM token"""
        getfcmtoken = FcmToken.objects.filter(user_id=manager_id).last()
        return getfcmtoken.fcm_token if getfcmtoken else None
    
    def send_push_notification(self, title, body, manager_id, types, order_id, order_type):
        import time
        start_time = time.time()
        
        # Get token with caching
        tokens = self.get_user_fcm_token(manager_id)
        if not tokens:
            logger.warning(f"No FCM token found for user {manager_id}")
            return JsonResponse({"success": False, "message": "No valid token available for notification."})

        try:
            app = firebase_admin.get_app("melcom-2a501")

            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                token=tokens
            )
            data = messaging.send(message, app=app)

            storen = Notification(title=title, message=body, user_id=manager_id, type=types, order_id=order_id,
                                order_status=order_type)
            storen.save()

            # Update order status if needed and invalidate any related caches
            if order_type == 6:
                Notification.objects.filter(order_id=order_id).update(order_status=order_type)
                # Invalidate any order-related caches
                invalidate_prefix(f"order_{order_id}")
                invalidate_cache_pattern(f"notification_order_{order_id}")
            
            # Log performance metrics
            execution_time = time.time() - start_time
            logger.debug(f"Push notification sent in {execution_time:.2f}s to user {manager_id}")
            
            return JsonResponse({
                "success": True, 
                "message": "Push notification sent successfully.",
                "execution_time_ms": round(execution_time * 1000, 2),
                "notification_id": storen.id
            })

        except firebase_admin.exceptions.FirebaseError as e:
            logger.error(f"Firebase error while sending notification to {manager_id}: {str(e)}")
            error_message = f"Push notification failed: {str(e)}"
            return JsonResponse({"success": False, "message": error_message})

        except Exception as e:
            logger.error(f"Unexpected error while sending notification to {manager_id}: {str(e)}", exc_info=True)
            error_message = f"Unexpected error occurred: {str(e)}"
            return JsonResponse({"success": False, "message": error_message})

class SendTestnotification(GenericAPIView):
    # Initialize Firebase only once
    if not firebase_admin._apps.get("melcom-2a501"):
        cred = credentials.Certificate('melcom-2a501-59a077dbe1df.json')
        firebase_admin.initialize_app(cred, name="melcom-2a501")
    
    @cache_result(timeout=300, key_prefix="test_fcm_token")
    def get_cached_token(self, user_id):
        """Get a user's FCM token with caching"""
        getfcmtoken = FcmToken.objects.filter(user_id=user_id).first()
        return getfcmtoken.fcm_token if getfcmtoken else None
    
    def post(self, request, format=None):
        import time
        start_time = time.time()
        
        # Try to get a token with fallbacks and caching
        token = None
        user_ids = [850, 737]  # List of user IDs to try
        
        for user_id in user_ids:
            token = self.get_cached_token(user_id)
            if token:
                logger.debug(f"Using FCM token from user {user_id}")
                break
        
        if not token:
            logger.warning("No valid FCM token found for test notification")
            return JsonResponse({"success": False, "message": "No valid token available for notification."})
        
        try:
            app = firebase_admin.get_app("melcom-2a501")
            
            # Customizable notification from request or defaults
            title = request.data.get('title', "Test Notification")
            body = request.data.get('body', "This is a test notification")
            
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                token=token
            )
            data = messaging.send(message, app=app)
            execution_time = time.time() - start_time
            
            # Log success
            logger.info(f"Test notification sent successfully in {execution_time:.2f}s")
            
            return JsonResponse({
                "success": True, 
                "message": f"Push notification sent: {data}",
                "execution_time_ms": round(execution_time * 1000, 2),
                "token": token[:10] + "..." if token else None
            })
            
        except firebase_admin.exceptions.FirebaseError as e:
            logger.error(f"Firebase error while sending test notification: {str(e)}")
            return JsonResponse({"success": False, "message": f"Firebase error: {str(e)}"})
            
        except Exception as e:
            logger.error(f"Unexpected error while sending test notification: {str(e)}", exc_info=True)
            return JsonResponse({"success": False, "message": f"Unexpected error: {str(e)}"})


class PrimeMemberPlanlist(GenericAPIView):
    serializer_class = PrimePlanSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        prime_member_plans = PrimeMemberPlan.objects.all()
        plan_data = []

        for prime_member_plan in prime_member_plans:
            queryset = PlanBenefits.objects.filter(plan_id=prime_member_plan.id)
            plan_benefits = PlanBenefitsSerializer(queryset, many=True).data

            product_data = {
                'plan_id': prime_member_plan.id,
                'plan_amount': prime_member_plan.plan_amount,
                'plan_validity': prime_member_plan.plan_validity,
                'plan_text': prime_member_plan.plan_text,
                'plan_recommanded': prime_member_plan.plan_recommanded,
                'created_at': prime_member_plan.created_at,
                'updated_at': prime_member_plan.updated_at,
                'benefits': plan_benefits,
                # Add other fields you want to include here
            }
            plan_data.append(product_data)

        return Response({'status': True, 'data': plan_data, 'msg': 'Success'}, status=status.HTTP_200_OK)

class PlanBenefitsView(GenericAPIView):
    serializer_class = PlanBenefitsSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        plan_id = request.data.get('plan_id')
        if plan_id is None:
            return Response({'status': False, 'msg': 'Missing plan id', 'data': None}, status=status.HTTP_200_OK)

        queryset = PlanBenefits.objects.filter(plan_id=plan_id)
        serializer = PlanBenefitsSerializer(queryset, many=True)

        if queryset.exists():
            return Response({'status': True, 'data': serializer.data, 'msg': 'Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'msg': 'Plan not found', 'data': None}, status=status.HTTP_200_OK)

class AddCardDetails(GenericAPIView):
    serializer_class = PlanBenefitsSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        card_number = request.data.get('card_number')
        card_name = request.data.get('card_name')
        card_month_year = request.data.get('card_month_year')
        user_id = request.user.id
        storen = UserCardDeatils(card_number = card_number,card_name=card_name,user_id = user_id,card_month_year=card_month_year)
        storen.save()
        return Response({'status': True, 'data': {}, 'msg': 'Success'}, status=status.HTTP_200_OK)

class CardListView(GenericAPIView):
    serializer_class = UserCarddetailsSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        card_details = UserCardDeatils.objects.filter(user_id = user_id)
        cardlist = UserCarddetailsSerializer(card_details,many=True).data
        if cardlist:
            return Response({'status': True, 'data': cardlist, 'msg': 'Success'}, status=status.HTTP_200_OK)
        else:
           return Response({'status': False, 'data': {}, 'msg': 'Data not found'}, status=status.HTTP_200_OK)


class CountryCodeList(GenericAPIView):
    serializer_class = CountryCodeSerializer
    def get(self, request, format=None):
        country_code = CountryCode.objects.all()
        code_list = CountryCodeSerializer(country_code, many=True).data
        return Response({'status': True, 'data': code_list, 'msg': 'Success'}, status=status.HTTP_200_OK)

class MySubscriptionPlanView(GenericAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    @cache_result(timeout=300, key_prefix="user_subscription")
    def get(self, request, format=None):
        user_id = request.user.id
        get_subs_plan = UserSubscription.objects.filter(user_id=user_id, status=1, payment_status=9).first()
        if get_subs_plan is None:
            return Response({'status': False, 'data': {}, 'msg': 'You are not a prime member'}, status=status.HTTP_200_OK)
        else:
            plan_data = UserSubscriptionSerializer(get_subs_plan).data

            prime_member_plans = PrimeMemberPlan.objects.filter(id=get_subs_plan.plan_id).first()

            queryset = PlanBenefits.objects.filter(plan_id=prime_member_plans.id)

            plan_benefits = PlanBenefitsSerializer(queryset, many=True).data

            upgrade_planfor = PrimeMemberPlan.objects.filter(plan_amount__gt=prime_member_plans.plan_amount)
            if upgrade_planfor:
                upgradeplan_data = []
                for prime_member_plan in upgrade_planfor:
                    queryset = PlanBenefits.objects.filter(plan_id=prime_member_plan.id)

                    plan_benefits = PlanBenefitsSerializer(queryset, many=True).data

                    product_dataupgrade = {
                        'plan_id': prime_member_plan.id,
                        'plan_amount': prime_member_plan.plan_amount,
                        'plan_validity': prime_member_plan.plan_validity,
                        'plan_text': prime_member_plan.plan_text,
                        'plan_recommended': prime_member_plan.plan_recommanded,
                        'created_at': prime_member_plan.created_at,
                        'updated_at': prime_member_plan.updated_at,
                        'benefits': plan_benefits,
                        # Add other fields you want to include here
                    }
                    upgradeplan_data.append(product_dataupgrade)

            else:
                upgradeplan_data = []

            product_data = {
                'plan_id': prime_member_plans.id,
                'plan_amount': prime_member_plans.plan_amount,
                'plan_validity': prime_member_plans.plan_validity,
                'plan_text': prime_member_plans.plan_text,
                'plan_recommended': prime_member_plans.plan_recommanded,
                'created_at': prime_member_plans.created_at,
                'updated_at': prime_member_plans.updated_at,
                'benefits': plan_benefits,
                # Add other fields you want to include here
            }

            purchase_plan = {}
            purchase_plan['subscription_plan'] = plan_data
            purchase_plan['plan_details'] = product_data
            purchase_plan['plan_upgrade_for'] = upgradeplan_data

            return Response({'status': True, 'data': purchase_plan, 'msg': 'Success'}, status=status.HTTP_200_OK)


class CustomerView(APIView):
    def get(self, request):
         return Response({'status': True, 'msg': 'Success'}, status=status.HTTP_200_OK)

class ChartView(APIView):
    @cache_result(timeout=900, key_prefix="monthly_user_data")
    def get(self, request):
        month1 = request.GET.get('month')
        year1 = request.GET.get('year')

        monthly_user_data = {}
        user_data = []
        current_date = date.today()
        if not month1:
            current_month = current_date.month
        else:
            current_month = int(month1)

        if not year1:
            current_year = current_date.year
        else:
            current_year = int(year1)
        my_list= []
        my_month= []
        my_calender=[]
        my_recieved_price=[]
        totals_by_month = {}
        completePercentageDonut=0
        cancelledPercentageDount=0
        labels = {}
        values= {}

        for month in range(1, 13):
            users = User.objects.annotate(month=ExtractMonth('created_at'),year=ExtractYear('created_at')).filter(month=month,year=current_year).count()
            calender_name=calendar.month_abbr[month]
            my_list.append(users)
            my_month.append(calender_name)

        context = {
            'labels': my_month,
            'values': my_list,

        }


        completeOrder= Order.objects.annotate(month=ExtractMonth('created_at'),year=ExtractYear('created_at')).filter( order_status_id = 6,month=current_month,year=current_year).count()

        rejectOrder= Order.objects.annotate(month=ExtractMonth('created_at'),year=ExtractYear('created_at')).filter( order_status_id = 7,month=current_month,year=current_year).count()

        cancelledOrder= Order.objects.annotate(month=ExtractMonth('created_at'),year=ExtractYear('created_at')).filter(order_status_merchant = 8,month=current_month,year=current_year).count()

        TotalOrder= Order.objects.annotate(month=ExtractMonth('created_at'),year=ExtractYear('created_at')).filter(Q(order_status_merchant = 8) | Q(order_status_id = 6) | Q(order_status_id = 7),month=current_month,year=current_year).count()

        cancelledOrderPercentage=0
        completeOrderPercentage=0
        rejectOrderPercentage=0


        if completeOrder:
            completeOrderPercentage= round((completeOrder/TotalOrder)*100,2);


        if cancelledOrder:
            cancelledOrderPercentage= round((cancelledOrder/TotalOrder)*100,2);

        if rejectOrder:
            rejectOrderPercentage= round((rejectOrder/TotalOrder)*100,2);

        dataDonut={
            'completeOrderPer':completeOrderPercentage if completeOrderPercentage else 0,
            'cancelledOrderPer':cancelledOrderPercentage if cancelledOrderPercentage else 0,
            'rejectOrderPer':rejectOrderPercentage if rejectOrderPercentage else 0,
            'completeOrder':completeOrder if completeOrder else 0,
            'cancelledOrder':cancelledOrder if cancelledOrder else 0,
            'rejectOrder':rejectOrder if rejectOrder else 0,
            'TotalOrder':TotalOrder if TotalOrder else 0,
            'current_month':calendar.month_name[current_month],
            'selected_month_id':current_month,
            'selected_year':current_year,
        }



        ####2nd graph data

        total_complete_price=0
        total_cancelled_price=0
        total_complete_price_value=0
        total_cancel_price_value=0
        total_price_value=0

        total_complete_price = Order.objects.annotate(month=ExtractMonth('created_at'),year=ExtractYear('created_at')).aggregate(total=Sum('total', filter=Q(order_status_id=6,month=current_month,year=current_year)))

        total_cancelled_price = Order.objects.annotate(month=ExtractMonth('created_at'),year=ExtractYear('created_at')).aggregate(total=Sum('total', filter=Q(order_status_merchant=8,month=current_month,year=current_year)))

        # total_cancelled_price = Order.objects.annotate(month=ExtractMonth('created_at'),total=Sum('total')).filter(order_status_merchant=8,month=current_month)


        totalPrice= Order.objects.annotate(month=ExtractMonth('created_at'),year=ExtractYear('created_at')).aggregate(total=Sum('total', filter=Q(Q(order_status_merchant=8) | Q(order_status_id=6),month=current_month,year=current_year)))

        # print(total_cancelled_price)
        if totalPrice['total']:
            total_price_value = Decimal(str(totalPrice['total'])).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)


        if total_complete_price['total']:
            completePercentageDonut= round((total_complete_price['total']/totalPrice['total'])*100,2);
            total_complete_price_value = Decimal(str(total_complete_price['total'])).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

        if total_cancelled_price['total']:
            cancelledPercentageDount= round((total_cancelled_price['total']/totalPrice['total'])*100,2);
            total_cancel_price_value = Decimal(str(total_cancelled_price['total'])).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

        dataDonutChart={
            'completePercentageDonut':completePercentageDonut if completePercentageDonut else 0,
            'cancelledPercentageDount':cancelledPercentageDount if cancelledPercentageDount else 0,
            'total_complete_price':total_complete_price_value if total_complete_price_value else 0,
            'total_cancelled_price':total_cancel_price_value if total_cancel_price_value else 0,
            'totalPrice' :total_price_value if total_price_value else 0,

        }

        ####1st Graph
        for month in range(1, 13):

            # recieved_price['total']=0

            # recieved_price['total']=0

            recieved_price = Order.objects.filter(
                Q(order_status_id=6,
                created_at__month=month, created_at__year=current_year)
            ).aggregate(
                total=ExpressionWrapper(
                    Coalesce(Cast(Sum('total'), IntegerField()), Value(0, output_field=IntegerField())),
                    output_field=IntegerField()

                )
            )['total']

            totals_by_month[month] = recieved_price
            # print(totals_by_month)

            # monthly_totals = Order.objects.annotate(month=ExtractMonth('created_at'))values('month').annotate(total_amount=Sum('amount'))


        for monthData,total in totals_by_month.items():
            calender_name=calendar.month_abbr[monthData]
            my_calender.append(calender_name)

            my_recieved_price.append(total)

            # my_month.append(calender_name)

        data = {
            'labels': my_calender,
            'values': my_recieved_price,

        }
        return Response({'status': True, 'msg': 'Success','data':context,'dataDonut':dataDonut,'dataDonutChart':dataDonutChart,'lineChart':data}, status=status.HTTP_200_OK)

def custom_404_error(request,exception):
    return render(request, '404.html', status=404)

# from .forms import AuthenticationForm  # Adjust the import based on your actual form structure


# class login_view(APIView):
#  def get(self, request,  ):
#     custom_auth_form = AuthenticationForm()
#     request.session.cycle_key()

#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, mobile=username, password=password)

#         if user is not None:
#             login(request, user)
#             # Reset failed login attempts on successful login
#             user.failed_login_attempts = 0
#             user.save()
#             return redirect('home')
#         else:
#             # Increment failed login attempts on unsuccessful login
#             if hasattr(request, 'user') and hasattr(request.user, 'failed_login_attempts'):
#                 request.user.failed_login_attempts += 1
#                 request.user.save()
#                 messages.error(request, 'Invalid username or password.')

#     return render(request, 'login.html' ,{'formcaptcha': custom_auth_form,'test':"monika"})

#     # return render(request, '/templates/admin/login.html', {'formcaptcha': custom_auth_form,'test':"monika"})


def custom_login_view(request, *args, **kwargs):
    response = auth_views.login(request, *args, **kwargs)
    print(response,"ouuuuu")

    # Check if the user account is locked
    if response.status_code == 403:
        return HttpResponseForbidden('Your account is locked. Kindly try again after sometime ')

    return response



# from django.contrib.auth import authenticate, login
# from django.shortcuts import render, redirect
# from .utils import reset_login_attempts, reset_lockout

# def login_view(request):
#     # Your login logic here
#     user = authenticate(username=request.POST['username'], password=request.POST['password'])
#     reset_login_attempts(user)
#     reset_lockout(user)

#     if user is not None:
#         login(request, user)

#         # Reset login attempts and lockout for the user
#         reset_login_attempts(user)
#         reset_lockout(user)

#         return redirect('dashboard')
#     else:
#         # Handle unsuccessful login
#         return render(request, 'login.html', {'error_message': 'Invalid credentials'})

