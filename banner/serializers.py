from rest_framework import serializers
from banner.models import PrivacyPolicy, TermsConditions, FAQ,ContactUs

class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = ['title', 'content']

class TermsConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsConditions
        fields = ['title', 'content']

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['title', 'content']

class CantactUsSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()
    another_phone = serializers.SerializerMethodField()
    whatsapp_number = serializers.SerializerMethodField()
    class Meta:
        model = ContactUs
        fields = ['id', 'name', 'email', 'phone', 'another_phone', 'whatsapp_number','timestamp']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Convert phone fields to int if they exist
        for field in ['phone', 'another_phone', 'whatsapp_number']:
            value = data.get(field)
            try:
                data[field] = int(value) if value is not None else None
            except (ValueError, TypeError):
                data[field] = None  # fallback if not convertible

        return data

    def get_phone(self, obj):
        if obj.phone:
            return f"+{obj.phone}"
        return obj.phone
    def get_another_phone(self, obj):
        if obj.another_phone:
            return f"+{obj.another_phone}"
        return obj.another_phone 
    def get_whatsapp_number(self, obj):
        if obj.whatsapp_number:
            return f"+{obj.whatsapp_number}"
        return obj.whatsapp_number          