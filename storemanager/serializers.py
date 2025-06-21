from rest_framework import serializers
from accounts.models import User
from accounts.utils import Util
from banner.models import Issues
from stores.models import Stores,AssignDeliveryBoy
from attendance.models import Attendance
from accounts.models import Address,OrderAddress
from product.models import Order,Product
from .selectors import get_user_by_mobile, is_storemanager_role # Added import

def is_storemanager(user): # This function might be redundant if is_storemanager_role from selectors is preferred
    return user.groups.filter(name='storemanager').exists()

class LoginSerializer(serializers.ModelSerializer):
  mobile = serializers.CharField(max_length=255)
  class Meta:
    model = User
    fields = ['mobile', 'password']

class ProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'email', 'full_name', 'mobile', 'alternate_mobile','employee_id','profile_image','birth_date']

class SendPasswordResetEmailSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=255)
    class Meta:
      fields = ['mobile']

    def validate(self, attr):
        mobile = attr.get('mobile')
        # Use the cached selector
        user = get_user_by_mobile(mobile=mobile) 

        if user:
            # Use the role check function from selectors or the local one
            # if is_storemanager(user): # or use the one from selectors:
            if is_storemanager_role(user):
                body = f'email {user.email} mobile {user.mobile} Full name {user.full_name}'
                # Send EMail
                data = {
                'subject':'Reset Your Password',
                'body':body,
                'to_email':user.email
                }
                Util.send_email(data)
                return user # Return the user object as before
            else: 
               raise serializers.ValidationError('You are not authorized for this action (not a Store Manager).')
        else:
            raise serializers.ValidationError('User with this mobile number not found.')

class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class UserOrderAddressSerializer(serializers.ModelSerializer):
     class Meta:
        model = OrderAddress
        fields = '__all__'
        

class StoreDetailSerializer(serializers.ModelSerializer):
  class Meta:
    model = Stores
    fields = ['id','name','city']          

class AddressSerializer(serializers.ModelSerializer):
  class Meta:
    model = OrderAddress
    fields = '__all__' 
class UserFullProfileSerializer(serializers.ModelSerializer):
   class Meta:
    model = User
    fields = ['profile_image']   

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class UserDefaultAddressSerializer(serializers.ModelSerializer):
     class Meta:
        model = Address
        fields = '__all__'

class GetProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__' 
class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
       model = User
       fields =  ['id','full_name','mobile']
class StoreAddressSerializer(serializers.ModelSerializer):
    class Meta:
       model = Stores
       fields = '__all__'

