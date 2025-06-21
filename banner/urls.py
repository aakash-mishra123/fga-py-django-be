from django.urls import path
from banner.views import PrivacyPolicyView, TermsConditionView, FAQView, ContactUsView

urlpatterns = [
    path('privacy-policy/', PrivacyPolicyView.as_view(), name="privacy-policy"),
    path('terms-condition/', TermsConditionView.as_view(), name="terms-condition"),
    path('faqs/', FAQView.as_view(), name="faqs"),
    path('contact_us/', ContactUsView.as_view(), name="contact_us"),
]
