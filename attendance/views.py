from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.views import View

from rest_framework.generics import GenericAPIView

import datetime

from accounts.models import User
from attendance.serializers import MarkAttendanceSerializers


class MarkAttendance(GenericAPIView):
    serializer_class = MarkAttendanceSerializers
    
    def post(self, request):
        user_id = request.user.id
        current_date = datetime.date.today()
        
        serializer = self.serializer_class(
            data=request.data, 
            context={
                'user_id': user_id, 
                'currentDate': current_date
            }
        )



