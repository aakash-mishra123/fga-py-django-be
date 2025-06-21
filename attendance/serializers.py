from attendance.models import Attendance
from rest_framework import serializers
import datetime


class MarkAttendanceSerializers(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

    def validate(self, data):
        print('############################################',self.context['user_id'])
        #userId = self.context['userid']
        # if data['entry_type'] == 'in':
        #     if Attandance.object.filter(user_id = userId, created_at = datetime.date.today()):