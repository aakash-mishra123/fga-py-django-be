from django.contrib.auth.models import Group, Permission
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group, Permission
from django.http import HttpResponseForbidden
# middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser
# middleware.py

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
# from axes.utils import reset
from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated

class AccountLockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        # Skip logic for unauthenticated users
        if not user.is_authenticated:
            response = self.get_response(request)
            return response
        print("User888:", user, "Is Authenticated:", user.is_authenticated, "Request User:", request.user)

        # Check if the user is locked
        if hasattr(user, 'is_locked') and user.is_locked:
            print("Lock Duration:")

            # Check if the lockout period is over
            lock_duration = timezone.now() - user.locked_at
            print("Lock Duration:", lock_duration.total_seconds(), "Locked At:", user.locked_at)

            if lock_duration.total_seconds() >= 60:  # 1 minute lockout period
                # Unlock the account
                print("Unlocking the account")
                user.is_locked = False
                user.failed_login_attempts = 0
                user.save()

                reset(username=user.username)
            else:
                # User is still locked, return a forbidden response
                print("Account still locked. Please try again later.")
                return HttpResponseForbidden("Account locked. Please try again later.")

        response = self.get_response(request)
        return response

class FailedLoginMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(request.user,"------==============")
        # Check if the user is attempting to log in
        if request.method == 'POST' and 'login' in request.path:

            # Assuming you have a custom user model with a field 'failed_login_attempts'
            if hasattr(request, 'user') and hasattr(request.user, 'failed_login_attempts'):
                # Check if the user has exceeded the allowed number of login attempts
                if request.user.failed_login_attempts >= 3:  # Adjust the allowed attempts as needed
                    messages.error(request, 'Account locked due to multiple failed login attempts.')
                    return redirect(reverse('login'))  # Redirect to your login view

        response = self.get_response(request)
        return response

class SingleSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Get the user's session key
            session_key = request.session.session_key

            active_sessions = Session.objects.filter(
                 session_key__contains = request.user.id,
                expire_date__gte=timezone.now(),
            ).exclude(session_key=session_key)

            # Terminate active sessions
            for session in active_sessions:
                session_data = session.get_decoded()
                print("Session Data:", session_data)
                session.delete()




class PermissionMiddleware:
    def __init__(self, request):
        self.request = request

    def __call__(self, request):
        sales_group = get_object_or_404(Group, name='Sales')

        # Check if the user is in the Sales group
        if self.request.user in sales_group.user_set.all():
            # Check if the user has the permission for the current request
            if not self.request.user.has_perm(self.request.META['PERMISSION_NAME']):
                return HttpResponseForbidden('You do not have permission to access this page.')
        else:
            # The user is not in the Sales group
            return HttpResponseForbidden('You do not have permission to access this page.')

        return None