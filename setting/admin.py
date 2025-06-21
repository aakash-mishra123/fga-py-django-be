from django.contrib import admin
from setting.models import OrderStatus, Report
from stores.models import Stores
from django.utils.html import format_html
# Register your models here.
from django.contrib import admin
from django.contrib.auth.mixins import PermissionRequiredMixin

from .models import OrderStatus
from django.urls import reverse

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from permissions_utils import get_group_permissions
# from rangefilter.filters import (
#     DateRangeFilterBuilder,

# )
from django.contrib.admin.views.main import ChangeList


class OrderStatusAdmin(admin.ModelAdmin,PermissionRequiredMixin ):

    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_orderstatus'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_orderstatus'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False


    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_orderstatus'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return False
        else:
            return False


    def has_delete_permission(self, request, obj=None):
        # user_group_permissions = get_group_permissions(request.user)
        # desired_permission_codename = 'delete_orderstatus'
        # if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
        #     return True
        # else:
            return False


    model = OrderStatus
    list_display=('title','created_at')
    order_count = OrderStatus.objects.count()
    list_per_page = 50
    search_fields = ['title']


    # def changelist_view(self, request, extra_context=None):

    #     list_per_page = int(request.GET.get('e', 5))
    #     # print(list_per_page)
    #     self.list_per_page = list_per_page
    #     if extra_context is None:
    #         extra_context = {}

    #     # Set the maximum value for the "Items per page" dropdown
    #     extra_context['list_per_page_choices'] =[3, 5, 50, 100]
    #     print(extra_context)
    #     return super().changelist_view(request, extra_context=extra_context)

    readonly_fields = ['created_at']
    # search_fields = ['title']
    fieldsets = [
        ('Status info', {"fields": ["title"]})]
    # list_filter = (
    #     ("created_at", DateRangeFilterBuilder()),

    #       # Range + QuickSelect Filter

    # )

class StoreFilter(admin.SimpleListFilter):
    title = 'Store Name'
    parameter_name = 'Store'  # This should match your search field name

    def lookups(self, request, model_admin):
        unique_categories = Stores.objects.values('name','id').distinct()
        store_choices = [
            (store['id'], store['name']) for store in unique_categories
        ]

        return store_choices

    def queryset(self, request, queryset):
        # Apply the filter based on the selected option
        selected_option = self.value()
        if selected_option:
            return queryset.filter(category_id=selected_option)
        return queryset

class ReportsAdmin(admin.ModelAdmin):

    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_report'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_report'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):

            return False

    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_report'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):

            return False


    def has_delete_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'delete_report'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return False
        else:
            return False

    actions = ['generate_report']

    def generate(self, obj=None):

        url = reverse('customer:report', kwargs={'reportType': obj})
        return format_html('<a class="button" href="{}">View Details</a>', url)

    def title_link(self, obj):
        url = 'javascript:void(0);'
        return format_html('<a href="{}" style="color:#212529;font-weight: 500;">{}</a>', url, obj.title)

    title_link.short_description = 'Title'

    model = Report
    list_display=('title_link','generate','created_at')
    readonly_fields = ['created_at']
    order_count = Report.objects.count()
    list_per_page = 100

    def changelist_view(self, request, extra_context=None):

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)

    search_fields = ['title']
    fieldsets = [
        ('Info', {"fields": ["title"]})]

admin.site.register(OrderStatus,OrderStatusAdmin)
admin.site.register(Report,ReportsAdmin)
