from django.contrib import admin
from django.urls import path, include
# from django.conf.urls import url, include
from attendance.views import MarkAttendance

urlpatterns = [
    path('mark-attendance', MarkAttendance.as_view()),



]
