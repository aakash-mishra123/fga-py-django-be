from django.contrib.auth.models import Group, Permission
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from setting.middleware import PermissionMiddleware


class MyView(View):
    def get(self, request):
        # Check if the user has the permission for this view
        if not request.user.has_perm('my_permission'):
            return HttpResponseForbidden('You do not have permission to access this page.')

        # Do something else

        return render(request, '/templates/admin/base.html')
