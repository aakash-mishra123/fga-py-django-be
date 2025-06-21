# Standard library imports
import requests
# Django core imports
from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import validate_email
from django.db import models
from django.http import JsonResponse
from django.urls import reverse
from django.utils.html import format_html
from django import forms
from django.contrib.auth.models import Group
import requests
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from permissions_utils import get_group_permissions
from custom_filters.filters import (
    DateRangeFilterBuilder,
)
import firebase_admin
from firebase_admin import credentials, messaging, initialize_app, get_app
# Local application imports
from accounts.models import User, UserSubscription, DeviceVersion, FcmToken
from banner.models import (
    HomeBanner, ContactUs, PrivacyPolicy, OfferBanners,
    Notification, TermsConditions, FAQ, Issues, Supports, DeliveryHelps
)
from permissions_utils import get_group_permissions


class BannerAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_homebanners'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_homebanners'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_homebanners'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'delete_homebanners'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False


    list_display = ('image_preview', 'title', 'slug', 'content', 'status', 'priority', 'edit_item')
    banner_count = HomeBanner.objects.count()
    search_fields = ['title']
    list_per_page = 100

    def changelist_view(self, request, extra_context=None):

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)

       # Define a custom method for the delete icon
    def edit_item(self, obj):
        edit_url = reverse("admin:banner_homebanner_change", args=[obj.id])  # Replace 'your_app_name' with your actual app name
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>', edit_url)

    def delete_item(self, obj):
        url = reverse("admin:banner_homebanner_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>',  url)

    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')


    def product_picture(self,obj):
        return format_html('<img src="{0}" width="100" />'.format(obj.banner.url))

class OfferBannerAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_homebanners'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_offerbanners'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_offerbanners'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'delete_offerbanners'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False



    list_display = ('image_preview','title','slug','content','priority','status','edit_item')

    banner_count = OfferBanners.objects.count()
    list_per_page = 100
    def changelist_view(self, request, extra_context=None):

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)
    search_fields =['title']
         # Define a 'title']
         # Define a custom method for the delete icon
    def edit_item(self, obj):
        edit_url = reverse("admin:banner_offerbanners_change", args=[obj.id])  # Replace 'your_app_name' with your actual app name
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>', edit_url)

    def delete_item(self, obj):
        url = reverse("admin:banner_offerbanners_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>',  url)


    # Delete icon method description
    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')

# class CustomNotificationForm(forms.ModelForm):
#     CUSTOM_CHOICES = (
#         ('1', 'Customer'),
#         ('2', 'Prime'),
#         ('3', 'Non Prime'),
#     )

#     users_group = forms.ChoiceField(
#         choices=CUSTOM_CHOICES,
#         required=True,
#     )

class TitleFilter(admin.SimpleListFilter):
    title = 'Title'
    parameter_name = 'title'  # This should match your search field name

    def lookups(self, request, model_admin):
        # Define the filter options
        unique_title = Notification.objects.values('title').distinct()

        title_choices = [
            (title['title'], title['title']) for title in unique_title
        ]

        return title_choices

    def queryset(self, request, queryset):
        # Apply the filter based on the selected option
        selected_option = self.value()
        if selected_option:
            return queryset.filter(title=selected_option)
        return queryset

class NotificationAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_notification'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_notification'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_notification'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        # user_group_permissions = get_group_permissions(request.user)
        # desired_permission_codename = 'delete_notification'
        # if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
        #     return True
        # else:
            return False


    # form = CustomNotificationForm
    list_display = ('title', 'user', 'timestamp','edit_item')
    fields = ('users_group','title' , 'type', 'message')
    list_filter = ('user',TitleFilter)
    banner_count = Notification.objects.count()
    list_per_page = 100
    search_fields=['title','user__full_name']

    def changelist_view(self, request, extra_context=None):

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)
         # Define a custom method for the delete icon

    def edit_item(self, obj):
        edit_url = reverse("admin:banner_notification_change", args=[obj.id])  # Replace 'your_app_name' with your actual app name
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>', edit_url)

    def delete_item(self, obj):
        url = reverse("admin:banner_notification_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>',  url)

    def save_model(self, request, obj, form, change):
        users_group = obj.users_group
        title = obj.title
        fcm_tokens = []
        message_body = obj.message
        success_count = 0
        userCount = 0
        
        # Firebase app initialization and notification sending logic
        try:
            app = get_app("melcom-2a501")
        except ValueError:
            cred = credentials.Certificate("melcom-2a501-59a077dbe1df.json")
            app = initialize_app(cred, name="melcom-2a501")

        try:
            if users_group == '1':
                users = User.objects.filter(is_active=1)
                for user in users:
                    token_obj = FcmToken.objects.filter(user_id=user.id,fcm_token__isnull=False).exclude(fcm_token__exact='').order_by('-created_at').first()
                    
                    if token_obj:
                        userCount += 1
                    if token_obj and token_obj.fcm_token and token_obj.fcm_token.strip():
                        Notification.objects.create(
                            title=title,
                            message=message_body,
                            user_id=user.id,
                            type=obj.type  # Make sure `obj` is defined and valid
                        )

                        # Create the Firebase message
                        message = messaging.Message(
                            notification=messaging.Notification(
                                title=title,
                                body=message_body,
                            ),
                            token=token_obj.fcm_token,
                        )

                        try:
                            response = messaging.send(message, app=app)
                            success_count += 1
                        except firebase_admin.exceptions.FirebaseError as e:
                            if 'Requested entity was not found' in str(e):
                                messages.warning(request, f"Invalid token for user {user.id}, deleting...")
                                token_obj.delete()
                            else:
                                messages.error(request, f"FCM send error for user {user.id}: {e}")
                        except Exception as e:
                            messages.error(request, f"Unexpected error for user {user.id}: {e}")
                if success_count > 0:
                    messages.success(request, f"Push notifications sent successfully to {success_count} users.")
                else:
                    messages.warning(request, "No push notifications were sent. No valid tokens found or all sends failed.")
            elif users_group == '2':
                subs = UserSubscription.objects.filter(status=1, payment_status=9, fcm_token__isnull=False)
                for sub in subs:
                    Notification.objects.create(title=title, message=message_body, user_id=sub.user.id, type=obj.type)
                    fcm_tokens.append(sub.fcm_token)

            elif users_group == '3':
                subs = UserSubscription.objects.filter(status=0, payment_status=0, fcm_token__isnull=False)
                for sub in subs:
                    Notification.objects.create(title=title, message=message_body, user_id=sub.user.id, type=obj.type)
                    fcm_tokens.append(sub.fcm_token)

        except firebase_admin.exceptions.FirebaseError as e:
            if 'Requested entity was not found' in str(e):
                messages.warning(request, f"Invalid token for user {user.id}, deleting...")
                token_obj.delete()
            else:
                messages.error(request, f"FCM error for user {user.id}: {e}")
        except Exception as e:
            messages.error(request, f"Unexpected error for user {user.id}: {e}")

    # Delete icon method description
    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')


class PrivacyPolicyAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_privacypolicy'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_privacypolicy'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_privacypolicy'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'delete_privacypolicy'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False



    list_display = ('title','content','edit_item')

    banner_count = PrivacyPolicy.objects.count()
    list_per_page = 100
    search_fields = ['title','content']
    def changelist_view(self, request, extra_context=None):

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)
         # Define a custom method for the delete icon
    def edit_item(self, obj):
        edit_url = reverse("admin:banner_privacypolicy_change", args=[obj.id])  # Replace 'your_app_name' with your actual app name
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>', edit_url)

    def delete_item(self, obj):
        url = reverse("admin:banner_privacypolicy_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>',  url)


    # Delete icon method description
    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')


class TermsConditionsAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_termsconditions'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_termsconditions'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_termsconditions'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'delete_termsconditions'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False


    list_display = ('title','content','edit_item')

    banner_count = TermsConditions.objects.count()
    list_per_page = 100
    search_fields = ['title','content']

    def changelist_view(self, request, extra_context=None):

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)
         # Define a custom method for the delete icon
    def edit_item(self, obj):
        edit_url = reverse("admin:banner_termsconditions_change", args=[obj.id])  # Replace 'your_app_name' with your actual app name
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>', edit_url)

    def delete_item(self, obj):
        url = reverse("admin:banner_termsconditions_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>',  url)


    # Delete icon method description
    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')


class FAQAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_faq'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_faq'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_faq'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'delete_faq'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False


    list_display = ('title','content','edit_item')

    banner_count = FAQ.objects.count()
    list_per_page = 100
    search_fields = ['title','content']

    def changelist_view(self, request, extra_context=None):

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)

         # Define a custom method for the delete icon

    def edit_item(self, obj):
        edit_url = reverse("admin:banner_faq_change", args=[obj.id])  # Replace 'your_app_name' with your actual app name
        return format_html('<a class="button" href="{}"><i class="fas fa-edit"></i></a>', edit_url)

    def delete_item(self, obj):
        url = reverse("admin:banner_faq_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>',  url)


    # Delete icon method description
    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')


class IssueAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_issues'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_issues'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_issues'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'delete_issues'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    list_display = ('title','created_at','edit_item')

    banner_count = Issues.objects.count()
    list_per_page = 100

    search_fields = ['title']
    list_filter = (
        ("created_at", DateRangeFilterBuilder()),
    )
    def changelist_view(self, request, extra_context=None):

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)


         # Define a custom method for the delete icon
    def edit_item(self, obj):
        edit_url = reverse("admin:banner_issues_change", args=[obj.id])  # Replace 'your_app_name' with your actual app name
        return format_html('<a class="button" href="{}"><i class="fas fa-edit"></i></a>', edit_url)

    def delete_item(self, obj):
        url = reverse("admin:banner_issues_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>',  url)


    # Delete icon method description
    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')

class DeliveryBoyHelp(admin.ModelAdmin):

    def has_add_permission(self, request):
        # Return False to hide the "Add" button
        return False 
        
    def get_availability(self, obj):
        return 'Pending' if obj.status == '0' else 'Resolved'
    
    get_availability.short_description = 'Status'

    def get_title(self, obj):
        return obj.additional_note
    
    get_title.short_description = 'Additional Note'

    list_display = ('issuetype','get_title','created_at','user_link','get_availability','edit_item')

    def user_link(self, obj):
        user_change_url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}" target="_blank">{}</a>', user_change_url, obj.user)
    user_link.short_description = 'User'

    banner_count = Issues.objects.count()
    list_per_page = 100

    search_fields = ['additional_note']
    list_filter = (
        ("created_at", DateRangeFilterBuilder()),
    )

    def edit_item(self, obj):
        edit_url = reverse("admin:banner_deliveryhelps_change", args=[obj.id])  # Replace 'your_app_name' with your actual app name
        return format_html('<a class="button" href="{}"><i class="fas fa-edit"></i></a>', edit_url)

    fieldsets = [
        (None, {"fields": ["issuetype", "additional_note", "user", "status"]}),
    ]

    def changelist_view(self, request, extra_context=None):
        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page
        extra_context = extra_context or {}
        extra_context['additional_note'] = 'Addination Note'

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)

    def delete_item(self, obj):
        url = reverse("admin:banner_deliveryhelps_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button" href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>', url)

    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')



class SuportNumber(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_issues'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_issues'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):        
            return False

    def has_delete_permission(self, request, obj=None):       
            return False

    list_display = ('support_number','status','created_at','edit_item')

    banner_count = Supports.objects.count()
    list_per_page = 100

    search_fields = ['support_number']
    list_filter = (
        ("created_at", DateRangeFilterBuilder()),
    )
    def changelist_view(self, request, extra_context=None):       

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)


         # Define a custom method for the delete icon
    def edit_item(self, obj):
        edit_url = reverse("admin:banner_supports_change", args=[obj.id])  # Replace 'your_app_name' with your actual app name
        return format_html('<a class="button" href="{}"><i class="fas fa-edit"></i></a>', edit_url)

    # def delete_item(self, obj):
    #     url = reverse("admin:banner_issues_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
    #     return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>',  url)


    # Delete icon method description
    # edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')    


class ContactUsAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_contactus'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_contactus'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_contactus'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'delete_contactus'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    list_display = ('id', 'name', 'phone', 'another_phone','whatsapp_number', 'email', 'edit_item')
    banner_count = ContactUs.objects.count()
    list_per_page = 100
    def changelist_view(self, request, extra_context=None):

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)

    search_fields = ['name','phone','email']

    # Define a custom method for the delete icon
    def edit_item(self, obj):
        edit_url = reverse("admin:banner_contactus_change", args=[obj.id])  # Replace 'your_app_name' with your actual app name
        return format_html('<a class="button" href="{}"><i class="fas fa-edit"></i></a>', edit_url)

    def delete_item(self, obj):
        url = reverse("admin:banner_contactus_delete", args=[obj.id])
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>',  url)


    # Delete icon method description
    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')


    def save_model(self, request, obj, form, change):
        if not str(obj.phone).isdigit() or len(str(obj.phone)) != 10:
            form.add_error('phone', 'Phone number must be 10 digits and contain only numbers.')

        try:
            validate_email(obj.email)
        except ValidationError:
            form.add_error('email', 'Invalid email format.')
            return  # Prevent saving if there are errors

        super().save_model(request, obj, form, change)




class DeviceVersionAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_deviceversion'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_deviceversion'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_deviceversion'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'delete_deviceversion'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    list_display = ('id', 'version', 'edit_item')

    list_per_page = 100
    def changelist_view(self, request, extra_context=None):

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)

    search_fields = ['verison']

    # Define a custom method for the delete icon
    def edit_item(self, obj):
        edit_url = reverse("admin:accounts_deviceversion_change", args=[obj.id])  # Replace 'your_app_name' with your actual app name
        return format_html('<a class="button" href="{}"><i class="fas fa-edit"></i></a>', edit_url)

    def delete_item(self, obj):
        url = reverse("admin:accounts_deviceversion_delete", args=[obj.id])
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>',  url)


    # Delete icon method description
    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')



admin.site.register(HomeBanner,BannerAdmin)
admin.site.register(OfferBanners,OfferBannerAdmin)
admin.site.register(PrivacyPolicy,PrivacyPolicyAdmin)
admin.site.register(TermsConditions,TermsConditionsAdmin)
admin.site.register(FAQ,FAQAdmin)
admin.site.register(Issues,IssueAdmin)
admin.site.register(DeliveryHelps,DeliveryBoyHelp)
admin.site.register(Supports,SuportNumber)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(ContactUs, ContactUsAdmin)
admin.site.register(DeviceVersion, DeviceVersionAdmin)


# Register your models here.