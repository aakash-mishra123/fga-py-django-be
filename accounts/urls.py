from django.urls import path, include
from accounts.views import ChangePasswordView,SkipPrime,AppVerion,RegisterOTPVerify,UserAccountDelete,TestMail,CheckWednesday,CheckDays,CustomerView,UserSocialRegisView,ChartView,PrimeMemberPlanlist,UserProfileRemoveView,UserUpdateProfileViewWithIMG,CountryCodeList,UserRegistrationView,MySubscriptionPlanView,PrimeMemberPlan,PlanBenefitsView,UserUpdateProfileImageView,SendTestnotification,StateList,TestNotifications, CityList,UserLoginView,GuestUserView,MergeTokenView,SendPasswordResetEmailView, VerifyOtpView, UserPasswordResetView, UserProfileView, UserUpdateProfileView, UserAddAddressView, GetAddressView, DeleteAddressView, UpdateAddressView, UserLogoutView, UserSocialLoginView, MakeDefaultAddressView, LoginVerifyOtp, LoginWithOtp
from . import views
from accounts.views import custom_404_error
from django.conf.urls import handler404
from django.urls import path


app_name = 'accounts'  # Define the app namespace


urlpatterns = [
    path('app_version/', AppVerion.as_view(), name="user.app_version"),
    path('register/', UserRegistrationView.as_view(), name="user.register"),
    # path('admin/login/', custom_login_view, name='login'),
    path('user_account_delete/', UserAccountDelete.as_view(), name="user.user_account_delete"),
    path('register_otp_verify/', RegisterOTPVerify.as_view(), name="user.register_otp_verify"),
    path('testmail/', TestMail.as_view(), name='testmail'),
    path('login/', UserLoginView.as_view(), name="user.login"),
    path('gust_user/', GuestUserView.as_view(), name="user.gust_user"),
    path('merge_token/', MergeTokenView.as_view(), name="user.merge_token"),
    path('social-register/', UserSocialLoginView.as_view(), name="user.register"),
    path('social-login/', UserSocialRegisView.as_view(), name="user.login"),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='user.forgot-password-email'),
    path('verify-otp/', VerifyOtpView.as_view(), name='user.verify-otp'),
    path('send-loginWith-otp/', LoginWithOtp.as_view(), name='user.loginWith-otp'),
    path('loginVerify-otp/', LoginVerifyOtp.as_view(), name='user.loginVerify-otp'),
    path('reset-password/', UserPasswordResetView.as_view(), name='reset-password'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('remove_profile_image/', UserProfileRemoveView.as_view(), name='remove_profile_image'),
    path('profile-update/', UserUpdateProfileView.as_view(), name='profile-update'),
    path('profile-update_withoutimg/', UserUpdateProfileViewWithIMG.as_view(), name='profile-update_withoutimg'),
    path('profile-image-update/', UserUpdateProfileImageView.as_view(), name='profile-image-update'),
    path('add-address/', UserAddAddressView.as_view(), name="user.add-address"),
    path('get-address/', GetAddressView.as_view(), name="user.get-address"),
    path('make-address-default/', MakeDefaultAddressView.as_view(), name="user.default-address"),
    path('delete-address/', DeleteAddressView.as_view(), name="user.delete-address"),
    path('update-address/', UpdateAddressView.as_view(), name="user.update-address"),
    path('skip_prime/', SkipPrime.as_view(), name="user.skip_prime"),
    path('logout/', UserLogoutView.as_view(), name="user.logout"),
    path('state_list/', StateList.as_view(), name="user.state_list"),
    path('cities_list/', CityList.as_view(), name="user.cities_list"),
    path('check_days/', CheckDays.as_view(), name="user.check_days"),
    path('check_wed/', CheckWednesday.as_view(), name="user.check_wed"),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('test_notification/', TestNotifications.as_view(), name="user.test_notification"),
    path('check_notification/', SendTestnotification.as_view(), name="user.check_notification"),
    path('prime_member_plan/', PrimeMemberPlanlist.as_view(), name="user.prime_member_plan"),
    path('plan_benefits/', PlanBenefitsView.as_view(), name="user.plan_benefits"),
    path('my_subscription_plan/', MySubscriptionPlanView.as_view(), name="user.my_subscription_plan"),
    path('country_code_list/', CountryCodeList.as_view(), name="user.country_code_list"),
    path('admin/accounts/',CustomerView.as_view(), name='customer_view'),
    path('ChartView/',ChartView.as_view(), name='ChartView'),
    path('admin/chartView/',ChartView.as_view(), name='ChartView'),
    # path('login_view/',login_view, name='login_view'),
]
handler404 = custom_404_error