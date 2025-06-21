from django.db import models
from accounts.models import User

# Create your models here.

class Attendance(models.Model):
    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance"
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role_type = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=500, blank=True, null=True)
    in_time = models.TimeField(auto_now=False, auto_now_add=False)
    out_time = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
          return str(self.user)