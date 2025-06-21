import csv
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import Address, User, UserSubscription
from banner.utils.push_notifications import send_push_notification
from django.urls import reverse
from django.shortcuts import redirect
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.shortcuts import redirect
from accounts.models import Address, User,CountryCode ,PrimeMemberPlan , PlanBenefits
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from django.contrib import admin
from django.db.models import Case, When, Value, F
from django.db.models.functions import Coalesce
from attendance.models import  Attendance
from django.db import models
from django.contrib.auth.forms import UserChangeForm
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from permissions_utils import get_group_permissions
from django.contrib import admin
from django.contrib.auth import login as auth_login
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.utils import timezone
from urllib.parse import urlencode
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user and reset failed login attempts on successful login.
        """
        user = super().authenticate(request, username, password, **kwargs)
        
        if user:
            user.failed_login_attempts = 0
            user.last_failed_login = None
            user.save()
            
        return user

    def lockout_user(self, user):
        # Lockout user after 3 failed attempts
        user.failed_login_attempts += 1
        user.last_failed_login = timezone.now()
        user.save()

        if user.failed_login_attempts >= 3:
            return True

        return False

class AddressInline(admin.StackedInline):

    model = Address
    can_delete = False
    list_display = ["bulding_name","city", "pincode", "deafult"]
    fieldsets = [
        ('Address', {"fields": ["bulding_name","house_no", "street_address","state","city", "pincode", "deafult"]}),
    ]

    extra = 0

class CustomerTypeFilter(admin.SimpleListFilter):
    title = 'User Type'
    parameter_name = 'user'  # This should match your search field name

    def lookups(self, request, model_admin):
        # Define the filter options
        return (

            ('storeboy', _('Store Boy')),
            ('deliveryboy', _('Delivery Boy')),

        )

    def queryset(self, request, queryset):
        # Apply the filter based on the selected option
        selected_option = self.value()
        if selected_option:
            return queryset.filter(role_type=selected_option)
        return queryset

from django import forms
class UserModalAdminForm(forms.ModelForm):
    class Meta:
        model = User  # Specify the model here
        fields = '__all__'

    custom_list_per_page = forms.IntegerField(
        required=False,
        label='Custom List Per Page',
        help_text='Enter a custom value or leave blank to use default.'
    )
from django.utils.http import urlencode


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide the password field
        self.fields['password'].label = ''
        self.fields['password'].widget.attrs['style'] = 'display:none'

class UserModalAdmin(BaseUserAdmin,PermissionRequiredMixin):

    form = CustomUserChangeForm

    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)


        desired_permission_codename = 'view_user'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_user'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)

        desired_permission_codename = 'add_user'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        # user_group_permissions = get_group_permissions(request.user)
        # desired_permission_codename = 'delete_user'
        # if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
        #     return True
        # else:
        return False

    # def get_list_per_page(self, request):
    #     # Get the custom_list_per_page value from the form
    #     custom_list_per_page = self.form(request.GET).data.get('custom_list_per_page')

    #     # Use the custom value if provided, otherwise use the default
    #     if custom_list_per_page:
    #         return int(custom_list_per_page)
    #     else:
    #         return super().get_list_per_page(request)

    # def changelist_view(self, request, extra_context=None):
    #     # Add the custom_list_per_page value to the template context
    #     extra_context = extra_context or {}
    #     extra_context['custom_list_per_page'] = self.form(request.GET).data.get('custom_list_per_page')
    #     return super().changelist_view(request, extra_context=extra_context)

    # def get_list_filter(self, request):
    #     # Get the current URL parameters
    #     params = dict(request.GET.items())

    #     # Check if 'groups__isnull' is in the URL parameters
    #     if 'groups__isnull' in params:
    #         # Remove 'is_admin', 'is_staff', and 'groups' from list_filter
    #         return ['groups']

    #     # Use the default list_filter
    #     return super().get_list_filter(request)

    def changelist_view(self, request, extra_context=None):
        # Add a link to toggle the 'groups__isnull' parameter in the admin header
        extra_context = extra_context or {}
        groups_isnull = request.GET.get('groups__isnull=True')

        # Dynamically construct the base URL for the User model changelist
        opts = self.model._meta
        base_url = reverse(
            'admin:%s_%s_changelist' % (opts.app_label, opts.model_name),
            current_app=self.admin_site.name,
        )

        toggle_url = f"{base_url}?{urlencode({'groups__isnull': not groups_isnull})}"

        extra_context['groups_isnull_toggle'] = format_html(
            '<a href="{}">Toggle Groups</a>',
            toggle_url
        )

        return super().changelist_view(request, extra_context=extra_context)

    def get_availability_status_display(self, obj):
        status_choices = {
            '1': 'Active',
            '0': 'Inactive',
        }
        toggle_html = (
            f'<label class="switch" data-url="{reverse("customer:userStatusUpdate", args=[obj.pk])}"'
            f' data-status="{obj.status}">'
            f'<input type="checkbox" {"checked" if obj.status == 1 else ""}>'
            f'<span class="slider round"></span>'
            f'</label>'
        )
        return format_html(toggle_html)

    get_availability_status_display.short_description = 'Status'


    # list_display = ["id", "full_name","mobile","birth_date","custom_info","is_admin","get_availability_status_display","edit_item"]
    list_display = ["id", "full_name","mobile","get_availability_status_display"]
    # Delete functionality
    # delete_item
    search_fields =['full_name','mobile']
    User_count = User.objects.count()
    # list_per_page = 50

    def get_list_filter(self, request):
        if 'groups__isnull' in request.GET:
            groups_isnull = request.GET.get('groups__isnull')
            if groups_isnull.lower() == 'false':
                return [ 'groups']
        return ['is_admin', 'is_staff']

 

    def changelist_view(self, request, extra_context=None):
        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        print("request.GET:", request.GET)

        if 'groups__isnull' in request.GET:
            groups_isnull = request.GET.get('groups__isnull', '').lower()
            groups_id_exact = request.GET.get('groups__id__exact', '')

            if groups_isnull == 'false' and groups_id_exact != '':
                print("yryryyyyr")
                # If 'groups__isnull' is 'False' and 'groups__id__exact' is present
                # Keep 'groups__isnull' as it is and 'groups__id__exact' in the URL
                return super().changelist_view(request, extra_context=extra_context)
            elif 'q' in request.GET and 'groups__isnull' not in request.GET:
                # If search button is clicked and 'groups__isnull' is not in URL, add it
                new_params = request.GET.copy()
                new_params['groups__isnull'] = 'False'
                # Retain the existing value of 'groups__id__exact' if available
                if groups_id_exact != '':
                    new_params['groups__id__exact'] = groups_id_exact
                # Construct the URL with updated parameters
                url = f"{reverse('admin:accounts_user_changelist')}?{new_params.urlencode()}"
                return HttpResponseRedirect(url)

        # Handle the case where 'groups__isnull' is present but no other conditions matched
        if 'groups__id__exact' in request.GET:
            groups_id_exact = request.GET.get('groups__id__exact', '')
            new_params = request.GET.copy()
            new_params['groups__isnull'] = 'False'
            # Retain the existing value of 'groups__id__exact' if available
            if groups_id_exact != '':
                new_params['groups__id__exact'] = groups_id_exact
            # Construct the URL with updated parameters
            url = f"{reverse('admin:accounts_user_changelist')}?{new_params.urlencode()}"
            return HttpResponseRedirect(url)

        # Handle the case where no conditions matched
        print("No condition matched")

        return super().changelist_view(request, extra_context=extra_context)


    actions = ['delete_selected_items']

      # Define a custom method for the delete icon
    def edit_item(self, obj):
        url = reverse("admin:accounts_user_change", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit" aria-hidden="true"></i></a>', url)
    def delete_item(self, obj):
        url = reverse("admin:accounts_user_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>', url)

    def custom_info(self, obj):
        attendance_id = obj.id
        attendance_record = Attendance.objects.filter(user_id=attendance_id).order_by('-id').first()
        status='-'
        # print(attendance_record.status)
        if attendance_record:
            if attendance_record.status=='OUT':
                status='Unavailable'
            else:
                status='Available'
        else:
            status='Unavailable'

        return status
        # You should replace 'availability' with the actual field or method from your UserModal model

    custom_info.short_description = 'Availability'

    # Delete icon method description
     # Delete icon method description
    # delete_item.short_description = format_html('<span class="delete-action-description">Action</span>')
    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')

    fieldsets = [
        # ("Change Password", {"fields": ["password"]}),
        ("Personal info", {"fields": ["profile_image","email","full_name", "mobile","alternate_mobile","birth_date","blood_group","vehicle_number","vehicle_purchase_date","vehicle_name","password"]}),
        ("Permissions", {"fields": ["is_staff","is_admin", 'is_active', 'groups', 'user_permissions',]}),
    ]

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
                {
                "classes": ["wide"],
                "fields": ["profile_image","email", "full_name", "password1", "password2", "mobile","alternate_mobile","birth_date","blood_group","vehicle_number","vehicle_purchase_date","vehicle_name"],
            },
        ),
    ]
    # search_fields = ["email","mobile","full_name"]
    ordering = ('-id',)
    # list_filter = ['is_admin']
    filter_horizontal = []
    inlines = [AddressInline]
    actions = ['export_as_csv']  # Add the export action

    # ... (other methods and attributes)

    def export_as_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="user_data.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Email', 'Full Name', 'Mobile', 'Is Admin'])  # Add more fields as needed

        for user in queryset:
            writer.writerow([user.id, user.email, user.full_name, user.mobile, user.is_admin])  # Add more fields

        return response

    export_as_csv.short_description = "Export selected users as CSV"  # Set the action description

class CountryCodeAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_countrycode'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_countrycode'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):
        # user_group_permissions = get_group_permissions(request.user)
        # desired_permission_codename = 'add_countrycode'
        # if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
        #     return True
        # else:
            return False

    def has_delete_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'delete_countrycode'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    list_display = ('country_code', 'country_name','edit_item')
    list_filter = ('country_code', 'country_name')
    User_count = CountryCode.objects.count()
    list_per_page = 100

    search_fields=['country_code','country_name']
      # Define a custom method for the delete icon

    def edit_item(self, obj):
        edit_url = reverse("admin:accounts_countrycode_change", args=[obj.id])  # Replace 'your_app_name' with your actual app name
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>', edit_url)

    def delete_item(self, obj):
        delete_url = reverse("admin:accounts_countrycode_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>', delete_url)

    def changelist_view(self, request, extra_context=None):

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)


    # Delete icon method description
    delete_item.short_description = format_html('<span class="delete-action-description">Action</span>')
    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')

class PrimeMemberPlanAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_primemamberplan'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_primemamberplan'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_primemamberplan'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'delete_primemamberplan'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def get_availability_status_display(self, obj):
        status_choices = {
            '1': 'Active',
            '0': 'Inactive',
        }
        toggle_html = (
            f'<label class="switch" data-url="{reverse("customer:primeStatusUpdate", args=[obj.pk])}"'
            f' data-status="{obj.status}">'
            f'<input type="checkbox" {"checked" if obj.status == 1 else ""}>'
            f'<span class="slider round"></span>'
            f'</label>'
        )
        return format_html(toggle_html)

    get_availability_status_display.short_description = 'Status'

    list_display = ('id','plan_amount', 'plan_amount','plan_text','plan_recommanded','get_availability_status_display','edit_item')
    User_count = PrimeMemberPlan.objects.count()
    list_per_page = 100
    search_fields =['plan_amount','plan_amount']

    def edit_item(self, obj):
        edit_url = reverse("admin:accounts_primememberplan_change", args=[obj.id])  # Replace 'your_app_name' with your actual app name
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>', edit_url)

    def changelist_view(self, request, extra_context=None):

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)




      #   Define a custom method for the delete icon
    def delete_item(self, obj):
        url = reverse("admin:accounts_primememberplan_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>', url)

    # Delete icon method description
    # delete_item.short_description = format_html('<span class="delete-action-description">Action</span>')

    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')

class PlanBenefitsAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_planbenefits'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_planbenefits'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_planbenefits'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'delete_planbenefits'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return False
        else:
            return False



    list_display = ('id','plan', 'plan_title','plan_content','prime_discount','market_discount','free_delivery_order','edit_item')
    User_count = PlanBenefits.objects.count()
    list_per_page = 100
    search_fields = ['plan__id','plan_title','plan_content']

    def edit_item(self, obj):
        edit_url = reverse("admin:accounts_planbenefits_change", args=[obj.id])  # Replace 'your_app_name' with your actual app name
        return format_html('<a class="button  " href="{}"><i class="fas fa-edit"></i></a>', edit_url)


    #   Define a custom method for the delete icon
    def delete_item(self, obj):
        url = reverse("admin:accounts_planbenefits_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button " href="{}"><i class="fa fa-trash" aria-hidden="true"></i></a>', url)

    # Delete icon method description
    # delete_item.short_description = format_html('<span class="delete-action-description">Action</span>')

    edit_item.short_description = format_html('<span class="delete-action-description">Action</span>')

    def changelist_view(self, request, extra_context=None):

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(User, UserModalAdmin)
admin.site.register(CountryCode, CountryCodeAdmin)
admin.site.register(PrimeMemberPlan, PrimeMemberPlanAdmin)
admin.site.register(PlanBenefits, PlanBenefitsAdmin)





