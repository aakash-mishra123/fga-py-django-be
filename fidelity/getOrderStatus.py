#---------------------------------
# kalkicode.com
# These methods have not been changed by our tools.
# getorderStatus
#----------------------------

# include script with functions

from .plugin_Ecom import get_order_status

from django.shortcuts import render
from django.http import HttpResponse
from .import plugin_Ecom, getOrderStatus, createOrder
from rest_framework import views
from rest_framework.generics import GenericAPIView
import requests
import urllib3
from rest_framework import status
from product.models import Product, CatalogCategory, CatalogSubCategory, Order, OrderItem, ProductBrand, Wishlist, OrderItem
import requests
from accounts.models import Address, User
import urllib3

urllib3.disable_warnings()

# getting response with given parameters
class getorderstatusview(GenericAPIView):
    def get(self, request, format=None):
            order_id  = request.GET.get('order_id')
            session_id  = request.GET.get('session_id')
            operation ="GetOrderStatus"
            language ="EN"
            merchant = "TEST_ECOM531"


            result = getOrderStatus.get_order_status(operation, language, merchant,order_id,session_id)
            if result:
                return HttpResponse( result, status=status.HTTP_200_OK)
            else:
                return HttpResponse({'status':False,'msg':'order not found', 'data' : []}, status=status.HTTP_404_OK)

        #SessionID