from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from banner.serializers import PrivacyPolicySerializer, TermsConditionsSerializer, FAQSerializer,CantactUsSerializer
from banner.models import PrivacyPolicy, TermsConditions, FAQ,ContactUs
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from fcm_django.models import FCMDevice


# Create your views here.

class PrivacyPolicyView(GenericAPIView):
    serializer_class = PrivacyPolicySerializer
    def get(self, format=None):
        try:
            privacy = PrivacyPolicy.objects.all()
            serializer = PrivacyPolicySerializer(privacy, many= True)
            return Response({'status':True, 'data':serializer.data, 'msg':'Success'})
        except ObjectDoesNotExist:
            return Response({'status': False,'data': '', 'msg' : 'Privacy Policy not found'})


class TermsConditionView(GenericAPIView):
    serializer_class = TermsConditionsSerializer
    def get(self, format=None):
        try:
            terms = TermsConditions.objects.all()
            serializer = TermsConditionsSerializer(terms,many = True)
            return Response({'status':True, 'data':serializer.data, 'msg':'Success'})
        except ObjectDoesNotExist:
            return Response({'status': False,'data': '', 'msg' : 'Terms and condition not found'})


class FAQView(GenericAPIView):
    serializer_class = FAQSerializer
    def get(self, format=None):
        try:
            faqs = FAQ.objects.all()
            serializer = FAQSerializer(faqs, many=True)
            return Response({'status':True, 'data':serializer.data, 'msg':'Success'})
        except ObjectDoesNotExist:
            return Response({'status': False, 'data': '', 'msg': 'Faq not found'})


class ContactUsView(GenericAPIView):
    serializer_class = CantactUsSerializer
    
    def get(self, format=None):
        try:
            contact = ContactUs.objects.first()
            if not contact:
                return Response(
                    {'status': False, 'data': '', 'msg': 'Contact details not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = self.serializer_class(contact)
            return Response(
                {'status': True, 'data': serializer.data, 'msg': 'Success'},
                status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return Response(
                {'status': False, 'data': '', 'msg': 'Contact details not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class NotificationAdmin(GenericAPIView):
    list_display = ['title', 'user', 'timestamp']
    actions = ['send_notification']

    def send_notification(self, request, queryset):
        notification_results = []
        
        for notification in queryset:
            devices = FCMDevice.objects.filter(user=notification.user)
            if devices.exists():
                devices.send_message(
                    title=notification.title, 
                    body=notification.message
                )
                notification_results.append({
                    'user': notification.user.id,
                    'devices_count': devices.count(),
                    'status': 'sent'
                })
                
        # Return results if needed