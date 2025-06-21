from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import calendar

from django.contrib import admin
from django.db import models
from django.forms.widgets import TextInput
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from datetime import date
from django.db.models import DateField
from django.core.exceptions import PermissionDenied

from rangefilter.filter import DateRangeFilter
from rangefilter.filters import (
    DateRangeFilter,
)
from django.utils.translation import gettext_lazy as _


from accounts.models import Address, User
from attendance.models import Attendance
from permissions_utils import get_group_permissions


class DateRangeFilter(admin.SimpleListFilter):
    title = _('Date Range')
    parameter_name = 'date_range'

    def lookups(self, request, model_admin):
        return (
            ('today', _('Today')),
            ('this_week', _('This Week')),
            ('this_month', _('This Month'))
        )

    def queryset(self, request, queryset):
        if self.value() == 'today':
            return queryset.filter(created_at__date=date.today())
        elif self.value() == 'this_week':
            start_of_week = date.today() - timedelta(days=date.today().weekday())
            end_of_week = start_of_week + timedelta(days=6)
            return queryset.filter(created_at__date__range=(start_of_week, end_of_week))
        elif self.value() == 'this_month':
            start_of_month = date.today().replace(day=1)
            end_of_month = (start_of_month + relativedelta(months=1)) - timedelta(days=1)
            return queryset.filter(created_at__date__range=(start_of_month, end_of_month))
        elif self.value() == 'custom':
            # You can implement your custom date range filter logic here
            from_date = request.GET.get('from_date')
            to_date = request.GET.get('to_date')
            if from_date and to_date:
                return queryset.filter(created_at__date__range=(from_date, to_date))
        return queryset


class UserFullNameFilter(admin.SimpleListFilter):
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





class AttendanceAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'view_attendance'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'change_attendance'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):
        user_group_permissions = get_group_permissions(request.user)
        desired_permission_codename = 'add_attendance'
        if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        # user_group_permissions = get_group_permissions(request.user)
        # desired_permission_codename = 'delete_attendance'
        # if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
        #     return True
        # else:
            return False


    model = Attendance
    list_filter = [DateRangeFilter]
    list_display = ('user', 'in_time','role_type','out_time', 'created_at')
    # ,'delete_item'
    readonly_fields = ['created_at']
    Attendance_count = Attendance.objects.count()
    list_per_page = 100
    search_fields =['user__full_name']

    def changelist_view(self, request, extra_context=None):

        list_per_page = int(request.GET.get('e', self.list_per_page))
        self.list_per_page = list_per_page

        if extra_context is None:
            extra_context = {}

        # Set the maximum value for the "Items per page" dropdown
        extra_context['list_per_page_choices'] = [50, 100, 200, 500]

        return super().changelist_view(request, extra_context=extra_context)

      # Define a custom method for the delete icon
    def delete_item(self, obj):
        url = reverse("admin:attendance_attendance_delete", args=[obj.id])  # Use the correct URL pattern for the delete view
        return format_html('<a class="button" href="{}">Delete</a>', url)

    # Delete icon method description
    delete_item.short_description = "Delete"

    search_fields = ['user__full_name']
    # list_filter = (UserFullNameFilter,)  # Use the custom filter

    #list_filter = (UserFullNameFilter,DateRangeFilterBuilder())
    # list_filter = [
    #     ("created_at", DateRangeFilter),
    #     UserFullNameFilter,
    #     ]
    change_list_template = 'admin/attendance/attendance/change_list.html'

    # def changelist_view(self, request, extra_context=None):

    #     list_per_page = int(request.GET.get('e', 50))
    #     # print(list_per_page)
    #     self.list_per_page = list_per_page
    #     if extra_context is None:
    #         extra_context = {}

    #     # Set the maximum value for the "Items per page" dropdown
    #     extra_context['list_per_page_choices'] =[50, 100, 200, 500]
    #     print(extra_context)

    #     return super().changelist_view(request, extra_context=extra_context)

    fieldsets = [
        ('Attendance info', {"fields": ["user", "in_time", "out_time"]}),
    ]


admin.site.register(Attendance, AttendanceAdmin)
