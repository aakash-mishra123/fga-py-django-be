from django.urls import path, include
from accounts.views import ChangePasswordView,CustomerView,ChartView,PrimeMemberPlanlist,UserProfileRemoveView,UserUpdateProfileViewWithIMG,CountryCodeList,UserRegistrationView,MySubscriptionPlanView,PrimeMemberPlan,PlanBenefitsView,UserUpdateProfileImageView,SendTestnotification,StateList,TestNotifications, CityList,UserLoginView,GuestUserView,MergeTokenView,SendPasswordResetEmailView, VerifyOtpView, UserPasswordResetView, UserProfileView, UserUpdateProfileView, UserAddAddressView, GetAddressView, DeleteAddressView, UpdateAddressView, UserLogoutView, UserSocialLoginView, MakeDefaultAddressView, LoginVerifyOtp, LoginWithOtp

urlpatterns = [
    path('admin/',ChartView.as_view(), name='ChartView'),
]