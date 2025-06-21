#---------------------------------
# kalkicode.com
# These methods have not been changed by our tools.
# createOrder
#----------------------------

# include script with functions
from .plugin_Ecom import create_order
from django.shortcuts import render
from django.http import HttpResponse
from .import plugin_Ecom, getOrderStatus, createOrder
from rest_framework import views
from rest_framework import status
from rest_framework.generics import GenericAPIView
import requests
import urllib3
from product.models import Product, CatalogCategory, CatalogSubCategory, Order, OrderItem, ProductBrand, Wishlist, OrderItem
import requests
from accounts.models import Address, User, PrimeMemberPlan,UserSubscription
from rest_framework.permissions import IsAuthenticated
from datetime import date, timedelta
import re
from datetime import datetime



# getting response with given parameters
class createorderView(GenericAPIView):
    def get(self, request, format=None):
        # Your logic to create an order using createOrder.py
        order_id = request.GET.get('order_id')
        if order_id:
            order_details = Order.objects.filter(order_id=order_id).first()
            serialized_orders = []
            # Loop through each order and append its data to the list
            # for order in order_details:
            user_address_details = Address.objects.filter(id=order_details.user_address_id_id).first()
            user_details = User.objects.filter(id=order_details.user_id).first()
            user_address123 =[]
            user_detailss =[]

            # Format user data
            user_details = User.objects.filter(id=order_details.user_id).first()
            user_address_details = Address.objects.filter(id=order_details.user_address_id_id).first()
            
            # Create user contact info dictionary
            user_contact_info = {
                "mobile": user_details.mobile,
                "full_name": user_details.full_name,
                "email": user_details.email
            }
            
            # Create shipping address dictionary
            shipping_address_info = {
                "user_address": user_address_details.bulding_name,
                "city": user_address_details.city,
                "pincode": user_address_details.pincode,
                "street_address": user_address_details.street_address,
                "state": user_address_details.state,
                "house_no": user_address_details.house_no
            }
            
            # Prepare serialized order data for API request
            serialized_orders = [{
                "order_id": order_details.order_id,
                "total": order_details.total,
                "user_address_id": order_details.user_address_id_id,
                "user_id": order_details.user_id,
                "user_address_details": [shipping_address_info],
                "user_detailss": [user_contact_info]
            }]
            Create_Order = "CreateOrder"
            EN = "EN"
            merchant= "TEST_ECOM531"
            amount = serialized_orders.total
            description = "order created"
            currency = '978'
            approve_url = "/testshopPageReturn.jsp"
            CancelURL = "/testshopPageReturn.jsp"
            decline_url = "/testshopPageReturn.jsp"
            order_type = "Purchase"
            shipping_country = "Ghana"
            delivery_period = 32
            merchant_ext_id = "E643C1426056"
            email = serialized_orders[0]['user_detailss'][0]['email']
            phone = serialized_orders[0]['user_detailss'][0]['mobile']
            shipping_city = serialized_orders[0]['user_address_details'][0]['city']
            shipping_state = serialized_orders[0]['user_address_details'][0]['state']
            shipping_zip_code = serialized_orders[0]['user_address_details'][0]['pincode']
            shipping_address = serialized_orders[0]['user_address_details'][0]['user_address']

            result = createOrder.create_order(Create_Order, EN,  merchant ,amount , currency,  description, approve_url, CancelURL, decline_url, order_type, email, phone, shipping_country,shipping_city, delivery_period, merchant_ext_id, shipping_state,shipping_zip_code, shipping_address)

            if result:
                return HttpResponse({'status':False,'msg':'order created ', 'data' : result}, status=status.HTTP_200_OK)
            else:
                return HttpResponse({'status':False,'msg':'order not found', 'data' : []}, status=status.HTTP_404_OK)
        else:
            return HttpResponse ({'status':False,'msg':'order not found', 'data' : []}, status=status.HTTP_200_OK)


class JoinPrimeView(GenericAPIView):
         permission_classes = [IsAuthenticated]
         def get(self, request, format=None):
                # Your logic to create an order using createOrder.py
                plan_id = request.GET.get('plan_id')
                user = request.user.id
                if UserSubscription.objects.filter(user_id = user,plan_id=plan_id,status=1):
                    return HttpResponse ({'status':False,'msg':'this plan already runing', 'data':[]})
                order_details = PrimeMemberPlan.objects.filter(id=plan_id).first()
                timestamp = str(int(datetime.timestamp(datetime.now())))
                input_string = order_details.plan_validity
                matches = re.search(r'\d+', input_string)
                number = int(matches.group())
                order_id = f"PRIME-{timestamp}"
                plan_amount = order_details.plan_amount
                plan_validity = order_details.plan_validity
                plan_expiredate = (date.today()+timedelta(days=number)).isoformat()
                plan_id = plan_id
                user_id = user
                purcshe_plan = UserSubscription(order_id=order_id,plan_amount=plan_amount,plan_validity=plan_validity,plan_expiredate=plan_expiredate,plan_id=plan_id,user_id=user_id)
                purcshe_plan.save()

                if order_details:

                    serialized_orders = []
                    # Loop through each order and append its data to the list
                    # for order in order_details:
                    user_address_details = Address.objects.filter(user_id=user).first()
                    user_details = User.objects.filter(id=user).first()
                    user_address123 =[]
                    user_detailss =[]

                    user_all_details ={
                            "mobile":user_details.mobile,
                            "full_name":user_details.full_name,
                            "email":user_details.email
                    }
                    user_detailss.append(user_all_details)
                    user_address={
                            "user_address":user_address_details.bulding_name,
                            "city":user_address_details.city,
                            "pincode":user_address_details.pincode,
                            "street_address":user_addressDetails.street_address,
                            "state":user_addressDetails.state,
                            "house_no":user_addressDetails.house_no
                    }
                    user_address123.append(user_address)
                    serialized_order = {
                            "order_id": order_id,
                            "total": order_details.plan_amount,
                            "user_address_id": user_address_details.id,
                            "user_id": user,
                            "user_address_details":user_address123,
                            "user_detailss":user_detailss
                            # Add more fields as needed
                        }
                    serialized_orders.append(serialized_order)
                    Create_Order = "CreateOrder"
                    EN = "EN"
                    merchant= "TEST_ECOM531"
                    amount = order_details.plan_amount,
                    description = "order created"
                    currency = '978'
                    approve_url = "/testshopPageReturn.jsp"
                    CancelURL = "/testshopPageReturn.jsp"
                    decline_url = "/testshopPageReturn.jsp"
                    order_type = "Purchase"
                    shipping_country = "Ghana"
                    delivery_period = 32
                    merchant_ext_id = "E643C1426056"
                    email = serialized_orders[0]['user_detailss'][0]['email']
                    phone = serialized_orders[0]['user_detailss'][0]['mobile']
                    shipping_city = serialized_orders[0]['user_address_details'][0]['city']
                    shipping_state = serialized_orders[0]['user_address_details'][0]['state']
                    shipping_zip_code = serialized_orders[0]['user_address_details'][0]['pincode']
                    shipping_address = serialized_orders[0]['user_address_details'][0]['user_address']

                    result = createOrder.create_order(Create_Order, EN,  merchant ,amount , currency,  description, approve_url, CancelURL, decline_url, order_type, email, phone, shipping_country,shipping_city, delivery_period, merchant_ext_id, shipping_state,shipping_zip_code, shipping_address)


                    if result:
                        return HttpResponse({'status':True,'msg':'order found','data':result})
                    else:
                        return HttpResponse({'status':False,'msg':'order not found', 'data':[]})
                else:
                    return HttpResponse ({'status':False,'msg':'order not found', 'data':[]})

urllib3.disable_warnings()
# order shipping address