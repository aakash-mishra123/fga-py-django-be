from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from storemanager.serializers import LoginSerializer,UserOrderAddressSerializer,UserFullProfileSerializer,ProfileSerializer,SendPasswordResetEmailSerializer,OrderSerializer,DashboardSerializer,StoreDetailSerializer,AddressSerializer,UserDefaultAddressSerializer,GetProductSerializer,UsernameSerializer,StoreAddressSerializer
from fulfillmentmanager.serializers import UserorderAddressSerializer,LoginSerializer,NotificationListSerializer,ProductistSerializer,RiderAddressSerializer,RiderDetailSerializer,GetProductSerializer,OrderSerializer,StoreAddressSerializer,UsernameSerializer,AllOrderListSerializer,StroreSerializer,DeliveryDetailsSerializer,StoreDetailSerializer,RejectResionSerializer,UserDefaultAddressSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from banner.models import Issues
from storeboy.serializers import StoreBoyAttendanceSerializer
from accounts.models import Address,User,FcmToken ,OrderAddress
from attendance.models import Attendance
from order.models import OrderLog
from stores.models import Stores,AssignDeliveryBoy,AssignStoreManagers,StoreInventory, AssignStoreBoy, ProductEtaTiming
from order.models import AssignOrderToDeliveryBoy,AssignOrderToStoreBoy
from product.models import Product, CatalogCategory, CatalogSubCategory, Order, OrderItem, ProductBrand, Wishlist, OrderItem, OrderRating
import time
from datetime import datetime,date
# from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from datetime import datetime, timedelta
from django.db.models import Avg
from banner.models import Notification
from attendance.models import Attendance
from django.db.models import Count, F
from django.db.models import Max
from geopy.distance import geodesic
from storemanager.cache_utils import cache_result, invalidate_cache_pattern
from concurrent.futures import ThreadPoolExecutor

# Generate Token Manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@cache_result(timeout=3600,key_prefix="store_manager")
def is_storemanager(user):
    return user.groups.filter(name='storemanager').exists()

class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request, format=None):
        serializer = LoginSerializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.data.get('mobile')
        password = serializer.data.get('password')
        user = authenticate(mobile=mobile, password=password)
        if user is not None:
            # Use cached function for checking storemanager status
            deliverboy = is_storemanager(user)
            if deliverboy:
                user_id = user.id
                # Cache store manager assignment check
                @cache_result(timeout=300, key_prefix=f'store_manager_assignment_{user_id}')
                def get_store_manager_assignment():
                    return AssignStoreManagers.objects.filter(user_id=user_id).first()
                
                store_manager = get_store_manager_assignment()
                if store_manager:
                    token = get_tokens_for_user(user)
                    login(request, user)
                    userData = ProfileSerializer(request.user)
                    userProfie =  userData.data
                    userProfie['token']= token
                    user_id =   userProfie['id']
                    # Cache FCM token lookup
                    @cache_result(timeout=300, key_prefix=f'fcm_token_{user_id}')
                    def get_fcm_token():
                        return FcmToken.objects.filter(user_id=user_id).first()
                    
                    chkdevice_id = get_fcm_token()
                    if chkdevice_id:
                        updatetoken = FcmToken.objects.filter(user_id = user_id).update(fcm_token = request.data.get('fcm_token'))
                        # Invalidate the cache since we updated the token
                        invalidate_cache_pattern(f'fcm_token_{user_id}')
                    else:
                        fcm = request.data.get('fcm_token')
                        device_id = request.data.get('device_id')
                        updatetoken = FcmToken(device_id = device_id,fcm_token = fcm, user_id =user_id)
                        updatetoken.save()
                    # update_fcm_token = User.objects.filter(mobile=mobile).update(fcm_token = request.data.get('fcm_token'))
                    return Response({'status':True, 'data': userProfie, 'msg':'Login successful'}, status=status.HTTP_200_OK)
                else:
                    return Response({'status':False, 'data': {}, 'msg' : 'No store allocated yet. Please contact to admin.'}, status=status.HTTP_200_OK)
            else:
                return Response({'status':False, 'data': {}, 'msg' : 'User Id is not registered for this store manager'}, status=status.HTTP_200_OK)
        else:
            return Response({'status':False, 'data':{},'msg' : 'Mobile no. or Password is not Valid'}, status=status.HTTP_200_OK)



class SendPasswordResetEmailView(GenericAPIView):
    serializer_class = SendPasswordResetEmailSerializer
    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if not serializer.is_valid():
            default_errors = serializer.errors
            new_error = {}
            for field_name, field_errors in default_errors.items():
                new_error[field_name] = field_errors[0]
                break
            return Response({'status':False, 'data':{}, 'msg':list(new_error.values())[0]})
        else:
            return Response({'status':True,'msg':'OTP has been sent. Please check your Email.', 'data' : serializer.data}, status=status.HTTP_200_OK)

class StoreManagerBoyView(GenericAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        user_id = request.user.id
        get_store_id = AssignStoreManagers.objects.filter(user_id = user_id).first()
        get_store_address = Stores.objects.filter(id = get_store_id.store_id).first()
        address_store = StoreAddressSerializer(get_store_address)
        serializer = ProfileSerializer(request.user)
        store_address = Address.objects.filter(user_id=user_id).first()
        address = UserDefaultAddressSerializer(store_address)
        profile = {}
        profile['profile'] = serializer.data
        profile['address'] = address.data
        profile['store_address'] = address_store.data
        return Response({'status':True, 'data': profile, 'msg':'Success'}, status=status.HTTP_200_OK)

class DashboardView(GenericAPIView):
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated]
    
    # @cached_function(timeout=60)  # Cache dashboard data for 60 seconds
    def get(self, request, format=None):
        user_id = request.user.id
        
        @cache_result(timeout=300, key_prefix=f'store_manager_{user_id}')
        def get_store_manager():
            return AssignStoreManagers.objects.filter(user_id=user_id).first()
            
        get_store_manager = get_store_manager()
        dashboard = {}

        if get_store_manager:
            store_id = get_store_manager.store_id
            
            @cache_result(timeout=300, key_prefix=f'store_details_{store_id}')
            def get_store_details():
                return Stores.objects.get(id=store_id)
                
            store_details = get_store_details()
            
            # Cache order queries with short timeout since orders change frequently
            @cache_result(timeout=30, key_prefix=f'dashboard_orders_{store_id}')
            def get_dashboard_orders():
                return Order.objects.filter(
                    Q(store_id=store_id) & 
                    Q(order_status_id__in=[1,2,3,4,5]) & 
                    Q(is_delete=0) & 
                    Q(payment_mode__in=[1, 2, 3]) & 
                    (Q(order_status_merchant__isnull=True) | Q(order_status_merchant=9))
                ).order_by('-id')
                
            getorder_list = get_dashboard_orders()
            
            @cache_result(timeout=60, key_prefix=f'dashboard_counts_{store_id}')
            def get_dashboard_counts():
                counts = {
                    'orderCount': Order.objects.filter(
                        Q(store_id=store_id) & 
                        Q(order_status_id__in=[1,2,3,4,5]) & 
                        Q(is_delete=0) & 
                        Q(payment_mode__in=[1, 2, 3]) & 
                        (Q(order_status_merchant__isnull=True) | Q(order_status_merchant=9))
                    ).count(),
                    'pendingorderCount': Order.objects.filter(
                        Q(store_id=store_id) & 
                        Q(order_status_id=1) & 
                        Q(is_delete=0) & 
                        Q(payment_mode__in=[1, 2, 3]) & 
                        (Q(order_status_merchant__isnull=True) | Q(order_status_merchant=9))
                    ).count(),
                    'storeboyCount': AssignStoreBoy.objects.filter(store_id=store_id).count(),
                    'storeboy_ids': list(AssignStoreBoy.objects.filter(store_id=store_id).values_list('user_id', flat=True)),
                    'total_store_boy_free': AssignStoreBoy.objects.filter(store_id=store_id, status='free').count(),
                    'total_store_boy_busy': AssignStoreBoy.objects.filter(store_id=store_id, status='busy').count()
                }
                return counts
                
            counts = get_dashboard_counts()
            
            orderCount = counts['orderCount']
            pendingorderCount = counts['pendingorderCount']
            storeboyCount = counts['storeboyCount']
            storeboy_ids = counts['storeboy_ids']
            total_store_boy_free = counts['total_store_boy_free']
            total_store_boy_busy = counts['total_store_boy_busy']
            
            current_date = date.today()
            date_string = current_date.strftime("%Y-%m-%d")
            
            @cache_result(timeout=300, key_prefix=f'attendance_{date_string}_{store_id}')
            def get_attendance():
                return (Attendance.objects
                        .filter(created_at__date=date_string, user_id__in=storeboy_ids)
                        .values('created_at__date')
                        .annotate(count=Count('id'))
                        .order_by('created_at__date')
                    )
                    
            skdhsd = get_attendance()
            absent_storeboy_count = len(storeboy_ids) - len(skdhsd)
            
            order_data = []

            for order in getorder_list:
                # Cache order details processing
                @cache_result(timeout=60, key_prefix=f'order_details_{order.id}')
                def process_order_details(order):
                    deliver_address = OrderAddress.objects.get(order_id_id=order.id)
                    order_serializer = DashboardSerializer(order).data
                    deliver_address_serializer = AddressSerializer(deliver_address).data
                    
                    if order.payment_mode == "1":
                        order_typepay = "Cash"
                    elif order.payment_mode == "2":
                        order_typepay = "POS"
                    else:
                        order_typepay = "Online"

                    if OrderAddress.objects.filter(order_id_id=order.id).exists():
                        get_delivery_address = OrderAddress.objects.get(order_id_id=order.id)
                        del_lat = get_delivery_address.latitude
                        del_long = get_delivery_address.longitude
                    else:
                        get_delivery_address = Address.objects.filter(user_id=order.user_address_id_id).first()
                        del_lat = 0.00
                        del_long = 0.00        

                    get_store_details = Stores.objects.filter(id=store_id).first()
                    if get_store_details is not None:
                        storelat = get_store_details.latitude
                        storelong = get_store_details.longitude
                        storedetails = StroreSerializer(get_store_details)
                    else:
                        storelat = 0
                        storelong = 0
                        
                    coords_1 = (storelat, storelong)
                    coords_2 = (del_lat, del_long)
                    distance = round(geodesic(coords_1, coords_2).kilometers)
                    
                    DISTANCE_TIME_MAPPING = [
                        (2, 8), (3, 9), (4, 10), (5, 11), (6, 12), (7, 13), (8, 15)
                    ]
                    
                    time = next(
                        (time for max_distance, time in DISTANCE_TIME_MAPPING if distance <= max_distance),
                        17
                    )
                    
                    @cache_result(timeout=300, key_prefix=f'max_eta_{order.id}')
                    def get_max_eta():
                        return (
                            CatalogSubCategory.objects
                            .filter(id__in=[
                                product.subcategory_id
                                for product in Product.objects.filter(
                                    id__in=OrderItem.objects.filter(order=order).values_list('product_id', flat=True)
                                )
                            ])
                            .aggregate(Max('extra_eta'))['extra_eta__max'] or 0
                        )
                        
                    overall_max_eta = get_max_eta()

                    eta_timing = ProductEtaTiming.objects.filter(store_id=store_id).first()

                    if eta_timing:
                        item_1_to_5_timing = int(eta_timing.item_1_to_5_timing)
                        item_6_to_15_timing = int(eta_timing.item_6_to_15_timing)
                        item_15_to_25_timing = int(eta_timing.item_15_to_25_timing)
                        item_25_above_timing = int(eta_timing.item_25_above_timing)
                    else:
                        item_1_to_5_timing = 0
                        item_6_to_15_timing = 0
                        item_15_to_25_timing = 0
                        item_25_above_timing = 0
                        
                    iteam_count = OrderItem.objects.filter(order=order).count()
                    overall_max_eta = overall_max_eta if overall_max_eta is not None else 0
                    time = time if time is not None else 0

                    if iteam_count <= 5:
                        dtime = f"{item_1_to_5_timing + time+overall_max_eta} mins"
                    elif iteam_count <= 15:
                        dtime = f"{item_6_to_15_timing + time+overall_max_eta} mins"
                    elif iteam_count <= 25:
                        dtime = f"{item_15_to_25_timing + time+overall_max_eta} mins"
                    else:
                        dtime =f"{item_25_above_timing + time+overall_max_eta} mins"

                    durations = dtime

                    # Cache rider/storeboy info for this order
                    @cache_result(timeout=300, key_prefix=f'delivery_boy_{order.id}')
                    def get_delivery_boy():
                        if AssignOrderToDeliveryBoy.objects.filter(order_id=order.id).exists():
                            rider_obj = AssignOrderToDeliveryBoy.objects.filter(order_id=order.id).first()
                            rider_user = User.objects.get(id=rider_obj.user_id)
                            return rider_user.full_name
                        return ''
                        
                    rider_name = get_delivery_boy()

                    @cache_result(timeout=300, key_prefix=f'store_boy_{order.id}')
                    def get_store_boy():
                        if AssignOrderToStoreBoy.objects.filter(order_id=order.id).exists():
                            boy_obj = AssignOrderToStoreBoy.objects.filter(order_id=order.id).first()
                            boy_user = User.objects.get(id=boy_obj.user_id)
                            return boy_user.full_name
                        return ''
                        
                    storeboy_name = get_store_boy()

                    order_accept_time = OrderLog.objects.filter(order_id=order.id, status__in=["Accepted"]).first()
                    order_picked_time = OrderLog.objects.filter(order_id=order.id, status="process order").first()
                    if order_accept_time:
                        order_serializer['order_received_on'] = order_picked_time.created_at.strftime('%I:%M %p') if order_picked_time else ''
                        order_serializer['accept_on'] = order_accept_time.created_at.strftime('%I:%M %p')
                        order_serializer['expected_delivery'] = (order_accept_time.created_at + timedelta(minutes=10)).strftime('%I:%M %p') if order_accept_time else ''
                    else:
                        order_serializer['order_received_on'] = ''
                        order_serializer['accept_on'] = ''
                        order_serializer['expected_delivery'] = ''

                    order_serializer['time'] = durations
                    order_serializer['payment_mode'] = order_typepay
                    order_serializer['assigned_rider'] = rider_name
                    order_serializer['assigned_storeboy_name'] = storeboy_name
                    order_serializer['delivery_address'] = deliver_address_serializer
                    
                    return order_serializer
                
                order_data.append(process_order_details(order))

            if order_data:
                dashboard['order_list'] = order_data
            else:
                dashboard['order_list'] = []

            dashboard['store_details'] = StoreDetailSerializer(store_details).data
            dashboard['total_order'] = orderCount
            dashboard['pending_order'] = pendingorderCount
            dashboard['total_storeboy'] = storeboyCount
            dashboard['available_storeboy'] = total_store_boy_free
            dashboard['busy_storeboy'] = total_store_boy_busy
            dashboard['leave_storeboy'] = absent_storeboy_count
            return Response({'status': True, 'data': dashboard, 'msg': 'Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'msg': 'Store manager not found'}, status=status.HTTP_200_OK)

class OrderDetailsView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    @cache_result(timeout=300,key_prefix=f'attendance_order_details')
    def post(self, request, format=None):
        order_id = request.data.get('order_id')
        user = request.user.id
        if Order.objects.filter(order_id=order_id).exists():
            getorder_details = Order.objects.get(order_id=order_id)
            orderdetail_serializer = OrderSerializer(getorder_details)
            get_delivery_address = Address.objects.get(id=getorder_details.user_address_id.id)
            delivery_address = UserDefaultAddressSerializer(get_delivery_address)
            user_name =  User.objects.filter(id= getorder_details.user.id)
            user_contact = OrderAddress.objects.filter(order_id_id = getorder_details.id).first()
            user_details = UsernameSerializer(user_name,many=True).data
            store_details = Stores.objects.filter(id = getorder_details.store.id)
            Stroe_address = StoreAddressSerializer(store_details,many=True).data
            order_accept_time = OrderLog.objects.filter(order_id =getorder_details.id,status = "Accepted").first()
            order_picktime_time = OrderLog.objects.filter(order_id =getorder_details.id,status = "process order").first()
            order_delivery_time = OrderLog.objects.filter(order_id =getorder_details.id,status = "delivered").first()
            order_rating = OrderRating.objects.filter(order_id =getorder_details.id).first()

            # iteam_count = OrderItem.objects.filter(order_id = getorder_details.id).count()
            # if iteam_count <= 5:
            #         durations = 30
            # elif iteam_count <= 15:
            #         durations = 35
            # elif iteam_count <= 25:
            #         durations = 45
            # else:
            #         durations =50

            if OrderAddress.objects.filter(order_id_id = order_id).exists():
                    get_delivery_address = OrderAddress.objects.get(order_id_id = order_id)
                    del_lat = get_delivery_address.latitude
                    del_long = get_delivery_address.longitude
            else:
                    get_delivery_address = Address.objects.filter(user_id = getorder_details.user_address_id_id).first()
                    del_lat = 0.00
                    del_long = 0.00        

            get_store_details = Stores.objects.filter(id=getorder_details.store_id).first()
            if get_store_details is not None:
                    storelat = get_store_details.latitude
                    storelong = get_store_details.longitude

                    storedetails = StroreSerializer(get_store_details)
            else:
                    storelat = 0
                    storelong = 0
            coords_1 = (storelat, storelong)
            coords_2 = (del_lat, del_long)
            distance = round(geodesic(coords_1, coords_2).kilometers)
            DISTANCE_TIME_MAPPING = [
                    (2, 8),
                    (3, 9),
                    (4, 10),
                    (5, 11),
                    (6, 12),
                    (7, 13),
                    (8, 15)
                ]

            time = next(
                    (time for max_distance, time in DISTANCE_TIME_MAPPING if distance <= max_distance),
                    17
                )
                

            overall_max_eta = (
                        CatalogSubCategory.objects
                        .filter(id__in=[
                            product.subcategory_id
                            for product in Product.objects.filter(
                                id__in=OrderItem.objects.filter(order_id=getorder_details.id).values_list('product_id', flat=True)
                            )
                        ])
                        .aggregate(Max('extra_eta'))['extra_eta__max'] or 0
                    )

                # time = 30
                # km_time = distance/time
                # totaltime = int(km_time*60)

            eta_timing = ProductEtaTiming.objects.filter(store_id=getorder_details.store_id).first()

            if eta_timing:
                    item_1_to_5_timing = int(eta_timing.item_1_to_5_timing)
                    item_6_to_15_timing = int(eta_timing.item_6_to_15_timing)
                    item_15_to_25_timing = int(eta_timing.item_15_to_25_timing)
                    item_25_above_timing = int(eta_timing.item_25_above_timing)
            else:
                    # Default values if no ProductEta found
                    item_1_to_5_timing = 0
                    item_6_to_15_timing = 0
                    item_15_to_25_timing = 0
                    item_25_above_timing = 0
            iteam_count = OrderItem.objects.filter(order_id=getorder_details.id).count()
            overall_max_eta = overall_max_eta if overall_max_eta is not None else 0
            time = time if time is not None else 0

            if iteam_count <= 5:
                    dtime = f"{item_1_to_5_timing + time+overall_max_eta} mins"
            elif iteam_count <= 15:
                    dtime = f"{item_6_to_15_timing + time+overall_max_eta} mins"
            elif iteam_count <= 25:
                    dtime = f"{item_15_to_25_timing + time+overall_max_eta} mins"
            else:
                    dtime =f"{item_25_above_timing + time+overall_max_eta} mins"

            durations = dtime

            if order_rating:
                rating = order_rating.rating
                msg = order_rating.messages
            else:
               rating = 0
               msg = ""

            if getorder_details.payment_mode == "1":
                order_typepay = "Cash"
            elif getorder_details.payment_mode == "2":
                 order_typepay = "POS"
            else:
                        order_typepay = "Online"

            if order_accept_time:
             expected_delivery = (order_accept_time.created_at + timedelta(minutes=durations)).strftime('%I:%M %p')
            else:
                expected_delivery =  (getorder_details.created_at + timedelta(minutes=durations)).strftime('%I:%M %p')
            if order_delivery_time:
                ex_time = order_delivery_time.created_at.strftime('%I:%M %p')
            else:
                ex_time = expected_delivery
            orderTimeline = {}  # Define the orderTimeline dictionary here
            # Convert 'created_at' to "hh:mm AM/PM" format
            if order_accept_time:
                    expected_delivery = (order_accept_time.created_at + timedelta(minutes=durations)).strftime('%I:%M %p')
            else:
                    # Handle the case where order_accept_time is None
                    expected_delivery = (getorder_details.created_at + timedelta(minutes=durations)).strftime('%I:%M %p')

            if order_picktime_time:
                    ex_time = order_picktime_time.created_at.strftime('%I:%M %p')
            else:
                    # Handle the case where order_picktime_time is None
                    ex_time = expected_delivery

            orderTimeline = {
                    'order_received_on': getorder_details.created_at.strftime('%I:%M %p'),
                    'accept_on': order_accept_time.created_at.strftime('%I:%M %p') if order_accept_time else '',
                    'picked_time': order_picktime_time.created_at.strftime('%I:%M %p') if order_picktime_time else '',
                    # 'expected_delivery': ex_time,
                    'expected_delivery': order_delivery_time.created_at.strftime('%I:%M %p')  if order_delivery_time else '',
                }


            order_items = OrderItem.objects.filter(order_id=getorder_details.id)
            if AssignOrderToDeliveryBoy.objects.filter(order_id = getorder_details.id):
                rider_namess = AssignOrderToDeliveryBoy.objects.filter(order_id = getorder_details.id).first()
                rider_namess = User.objects.get(id = rider_namess.user_id)
                rider_name = rider_namess.full_name
            else:
               rider_name = ''

            if AssignOrderToStoreBoy.objects.filter(order_id = getorder_details.id):
                rider_namess = AssignOrderToStoreBoy.objects.filter(order_id = getorder_details.id).first()
                rider_namess = User.objects.get(id = rider_namess.user_id)
                storeboy_name = rider_namess.full_name
            else:
               storeboy_name = ''

            if order_items.exists():
                order_item_list = []
                final_price = 0
                for order_item in order_items:
                    product = Product.objects.get(id=order_item.product_id)
                    product_serializer = GetProductSerializer(product)
                    product_data = product_serializer.data
                    product_data['item_quantity'] = order_item.item_quantity
                    product_data['product_tags'] = 0
                    discount = order_item.discount_offer
                    price = float(product.price)
                    dis_price = (price * discount) / 100
                    final_price = float(product.price) - dis_price
                    if StoreInventory.objects.filter(product_id = order_item.product_id,store_id = getorder_details.store_id).exists():
                        inventprice = StoreInventory.objects.filter(product_id = order_item.product_id,store_id = getorder_details.store_id).first()
                        if inventprice.price == 0 or inventprice.price ==None:
                            
                            # price = product.price
                            price = str(final_price)
                        else:
                            price = str(final_price)
                    else:
                        price = str(final_price)
                    product_data['price'] = price
                    order_item_list.append(product_data)
            else:
                order_item_list = ""

            prolist = {}
            prolist['order_details'] = orderdetail_serializer.data
            prolist['order_details']['rating'] = rating
            prolist['order_details']['rating_message'] =msg
            prolist['order_details']['assigned_rider'] = rider_name
            prolist['order_details']['assigned_storeboy_name'] = storeboy_name
            prolist['order_details']['payment_mode'] = order_typepay
            prolist['order_details']['order_date_time'] = getorder_details.created_at.strftime("%Y-%m-%d %I:%M %p")
            prolist['order_details']['delivery_charges'] = 0
            prolist['customer_details'] = user_details[0]
            prolist['customer_details']['mobile'] = user_contact.contact_number
            prolist['store_address'] = Stroe_address[0]
            prolist['order_item'] = order_item_list
            prolist['delivery_address'] = delivery_address.data
            prolist['order_timeline'] = orderTimeline

            return Response({'status': True, 'msg': ' Successfully', 'data': prolist}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'msg': 'This order Id does not exist', 'data': {}}, status=status.HTTP_200_OK)

class MyTeamList(GenericAPIView):
    permission_classes = [IsAuthenticated]
    @cache_result(timeout=120, key_prefix='team_list')
    def get(self, request, format=None):
        user_id = request.user.id

        fulfillment_manager = AssignStoreManagers.objects.filter(user_id=user_id).first()

        if not fulfillment_manager:
            return Response({'status': False, 'data': {}, 'msg': 'Store manager not found'}, status=status.HTTP_200_OK)

        store_id = fulfillment_manager.store_id
        getdelivery_boy = AssignStoreBoy.objects.filter(store_id=store_id)
        if getdelivery_boy:
            myteam = []
            for store_user_id in getdelivery_boy:
                username = User.objects.filter(id=store_user_id.user_id).first()
                userimage = UserFullProfileSerializer(username).data
                total_delivery = OrderLog.objects.filter(user_id = store_user_id.user_id, status = 'Ready to pickup').count()
                if username:
                    team_member = {
                        'id': username.id,
                        'name': username.full_name,
                        'mobile_number': username.mobile,
                        'profile_image': userimage.get('profile_image', None),
                        'status': store_user_id.status,
                        'total_deliveries': total_delivery
                    }
                    myteam.append(team_member)

            return Response({'status': True, 'data': myteam, 'msg': 'My team list'}, status=status.HTTP_200_OK)
        else:
           return Response({'status': False, 'data': [], 'msg': 'Data not found'}, status=status.HTTP_200_OK)

class StoreBoyProfile(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RiderDetailSerializer,RiderAddressSerializer
    @cache_result(timeout=300, key_prefix=f'storeboy_profile')
    def post(self, request, format=None):
        user_id = request.user.id
        rider_id = request.data.get('storeboy_id')
        if User.objects.filter(id=rider_id):
            get_rider_details = User.objects.filter(id=rider_id).first()
            joindatett = AssignStoreBoy.objects.filter(user_id= get_rider_details.id).first()
            if joindatett:
                joindate = AssignStoreBoy.objects.filter(user_id= get_rider_details.id).first()
            else:
                joindate = " "
            rider_details = RiderDetailSerializer(get_rider_details).data
            rider_address = Address.objects.filter(user_id= rider_id).first()
            address = RiderAddressSerializer(rider_address).data
            total_delivery = OrderLog.objects.filter(user_id = rider_id, status = 'Ready to pickup').count()
            total_delivery_un = OrderLog.objects.filter(user_id = rider_id, status = 'process order').count()
            detailsreder = {}
            detailsreder['rider_details'] = rider_details
            detailsreder['rider_details']['blood_group'] = get_rider_details.blood_group
            detailsreder['rider_details']['rating'] = '4.5'
            detailsreder['rider_details']['joining_date'] = joindate.created_at
            detailsreder['rider_details']['dob'] = get_rider_details.birth_date
            detailsreder['rider_details']['rider_address'] = address
            detailsreder['total_delivery'] = total_delivery
            detailsreder['unsucessfully_delivery'] = total_delivery_un

            return Response({'status': True, 'data': detailsreder, 'msg': 'Riders details'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'data': {}, 'msg': 'Riders not found'}, status=status.HTTP_200_OK)

class StoreAttendance(GenericAPIView):
    serializer_class = StoreBoyAttendanceSerializer
    permission_classes = [IsAuthenticated]
    @cache_result(timeout=300, key_prefix=f'attendance_store')
    def post(self, request, format=None):
        user_id = request.data.get('storeboy_id')

        if Attendance.objects.filter(user_id=user_id).exists():
            month = request.data.get('month')
            year = request.data.get('year')

            deliveryboy_attendance = Attendance.objects.filter(user_id=user_id)

            if month and year:
                month_with_day = f"{year}-{month}-01"
                month_date = datetime.strptime(month_with_day, "%Y-%m-%d")
                deliveryboy_attendance = deliveryboy_attendance.filter(
                    created_at__year=month_date.year,
                    created_at__month=month_date.month,
                )

            attendance_list = StoreBoyAttendanceSerializer(deliveryboy_attendance, many=True)
            return Response({'status': True, 'msg': 'Attendance list', 'data': attendance_list.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'msg': 'Data not found', 'data': []}, status=status.HTTP_200_OK)


def get_user_data(user_id):
    user = User.objects.filter(id=user_id).first()
    return {
        'user': user,
        'profile_data': UserFullProfileSerializer(user).data if user else {}
    }

def get_storeboy_data(user_id):
    return AssignStoreBoy.objects.filter(user_id=user_id).first()


def get_orders_data(user_id):
    orders = OrderLog.objects.filter(user_id=user_id, status='Ready to pickup')
    result = []
    for order in orders:
        order_obj = Order.objects.filter(id=order.order_id).first()
        if order_obj:
            order_serialized = OrderSerializer(order_obj).data
            result.append({
                'order_id': order.order_id,
                'status': 1,
                'date': 1,
                'rating': '5',
                'orderslist': order_serialized
            })
    return result

def build_team_member(user_data, storeboy_data, orders):
    user = user_data['user']
    profile_data = user_data['profile_data']
    if not user or not storeboy_data:
        return None

    return {
        'id': user.id,
        'name': user.full_name,
        'mobile_number': user.mobile,
        'profile': profile_data.get('profile_image'),
        'status': storeboy_data.status,
        'rating': 5,
        'joined_on': user.created_at,
        'delivered_orders': orders
    }
class StoreDetails(GenericAPIView):
    permission_classes = [IsAuthenticated]
    # Your GET method with threading
def get(self, request, format=None):
    rider_id = request.GET.get('storeboy_id')

    if not User.objects.filter(id=rider_id).exists():
        return Response({'status': False, 'data': {}, 'msg': 'Data not found'}, status=status.HTTP_200_OK)

    with ThreadPoolExecutor() as executor:
        future_user = executor.submit(get_user_data, rider_id)
        future_storeboy = executor.submit(get_storeboy_data, rider_id)
        future_orders = executor.submit(get_orders_data, rider_id)

        user_data = future_user.result()
        storeboy_data = future_storeboy.result()
        orders = future_orders.result()

    team_member = build_team_member(user_data, storeboy_data, orders)

    if team_member:
        return Response({'status': True, 'data': team_member, 'msg': 'Riders details'}, status=status.HTTP_200_OK)
    else:
        return Response({'status': False, 'data': {}, 'msg': 'Data not found'}, status=status.HTTP_200_OK)

class NewOrderList(GenericAPIView):
    serializer_class = StoreDetailSerializer  # Use the correct serializer
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user_id = request.user.id
        search = request.GET.get('search')
        fulfillment_manager = AssignStoreManagers.objects.filter(user_id=user_id).first()

        if not fulfillment_manager:
            return Response({'status': False, 'data': {}, 'msg': 'Fulfillment manager not found'}, status=status.HTTP_200_OK)

        store_id = fulfillment_manager.store_id
        if not search:
            orders = Order.objects.filter(store_id=store_id,order_status_id__in=[1, 5]).order_by('-id')
        else:
            orders = Order.objects.filter(order_id__icontains=search,order_status_id__in=[1, 5]).order_by('-id')

        if not orders:
            return Response({'status': False, 'data': [], 'msg': 'Orders not found'}, status=status.HTTP_200_OK)

        order_list = []

        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            order_item_list = []
            if order.payment_mode == "1":
                      order_typepay = "Cash"
            elif order.payment_mode == "2":
                        order_typepay = "POS"
            else:
                        order_typepay = "Online"

            final_price = 0
            for order_item in order_items:
                product = Product.objects.get(id=order_item.product_id)
                discount = order_item.discount_offer
                price = float(product['price'])
                dis_price = (price * discount) / 100
                final_price = float(product['price']) - dis_price
                serializer = GetProductSerializer(product)
                product_data = serializer.data
                product_data['item_quantity'] = order_item.item_quantity
                product_data['product_tags'] = 0
                product_data['price'] = final_price
                order_item_list.append(product_data)

            order_details = OrderSerializer(order).data
            order_details['payment_mode'] = order_typepay
            order_details['time'] = '03:00 min'
            order_details['order_items'] = order_item_list
            order_list.append(order_details)

        response_data = {'status': True, 'data': {'order_list': order_list}, 'msg': 'Success'}
        return Response(response_data, status=status.HTTP_200_OK)

class OrderListAll(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user_id = request.user.id
        search = request.GET.get('search')
        rating = request.GET.get('rating')
        payment_mode = request.GET.get('payment_mode')
        order_status = request.GET.get('order_status')
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")
        fulfillment_manager = AssignStoreManagers.objects.filter(user_id=user_id).first()

        if not fulfillment_manager:
            return Response({'status': False, 'data': {}, 'msg': 'Store manager not found'}, status=status.HTTP_200_OK)

        store_id = fulfillment_manager.store_id
        # orders = Order.objects.filter(store_id=store_id).order_by('-updated_at')
        orders = Order.objects.filter(Q(store_id=store_id) & Q(is_delete=0) & Q(payment_mode__in=[1, 2, 3]) & (Q(order_status_merchant__isnull=True) | Q(order_status_merchant=9))).order_by('-updated_at')

        if search:
            orders = orders.filter(order_id__icontains=search)

        if order_status:
            orders = orders.filter(order_status_id=order_status)

        if rating:
            if rating == '2':
                orders = orders.filter(orderrating__rating__in=['1', '2'])
            elif rating == '3':
                orders = orders.filter(orderrating__rating__in=['3', '4'])
            elif rating == '5':
                orders = orders.filter(orderrating__rating__in=['4', '5'])
            elif rating == '0':
                orders = orders.filter(orderrating__rating=None)

        if payment_mode:
            if payment_mode == '1':
                orders = orders.filter(payment_mode='1')
            elif payment_mode == '2':
                orders = orders.filter(payment_mode='2')
            elif payment_mode == '3':
                orders = orders.filter(payment_mode='3')

        if from_date and to_date:
                orders = orders.filter(created_at__date__gte=from_date,  # Use ',' to separate conditions within a single Q object
                created_at__date__lte=to_date)

        all_orderlist = AllOrderListSerializer(orders, many=True).data

        for order_list in all_orderlist:
            order_id = order_list['id']

            if order_list['payment_mode'] == "1":
                order_typepay = "Cash"
            elif order_list['payment_mode'] == "2":
                order_typepay = "POS"
            elif order_list['payment_mode'] == "3":
                order_typepay = "Online"

            if order_list['delivery_boy_id'] == 0:
                delivery = ""
            else:
                deliveryname = User.objects.filter(id=order_list['delivery_boy_id']).first()
                delivery = deliveryname.full_name

            orderrating = OrderRating.objects.filter(order_id=order_id).aggregate(average_rating=Avg('rating'))
            rating = orderrating.get('average_rating', None) if orderrating and rating != '0' else None

            order_list['payment_mode'] = order_typepay
            order_list['delivery'] = delivery
            order_list['review'] = rating

        return Response({'status': True, 'data': all_orderlist, 'msg': 'Successfully'}, status=status.HTTP_200_OK)

class InventoryListnew(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user_id = request.user.id
        search = request.GET.get('search')
        fulfillment_manager = AssignStoreManagers.objects.filter(user_id=user_id).first()

        if not fulfillment_manager:
                return Response({'status': False, 'data': {}, 'msg': 'Fulfillment manager not found'}, status=status.HTTP_200_OK)

        store_id = fulfillment_manager.store_id
        inventory_pro = StoreInventory.objects.filter(store_id=store_id,status=1).order_by('-updated_at')
        product_list = []

        for store_pro in inventory_pro:
                get_product = Product.objects.filter(id=store_pro.product_id).first()

                if get_product is not None:  # Check if a product was found
                    get_category_name = CatalogCategory.objects.get(id=get_product.category_id)
                    product_data = {
                        'product_id': get_product.id,
                        'product_name': get_product.product_name,
                        'category_id': get_product.category_id,
                        'category_name': get_category_name.name,
                        'stock': store_pro.inventory,
                        'updated_date': store_pro.updated_at,
                    }
                    if search:
                        search = search.lower()
                        if search in get_product.product_name.lower() or search in get_category_name.name.lower():
                            product_data['store_id'] = store_id
                            product_list.append(product_data)
                    else:
                        product_data['store_id'] = store_id
                        product_list.append(product_data)

        return Response({'status': True, 'data': product_list, 'msg': 'Store product listing'}, status=status.HTTP_200_OK)

class InventoryList(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def binary_search(self, product_list, search):
        low, high = 0, len(product_list) - 1

        while low <= high:
            mid = (low + high) // 2
            mid_product = product_list[mid]['product_name'].lower()

            if mid_product == search:
                return mid
            elif mid_product < search:
                low = mid + 1
            else:
                high = mid - 1

        return -1

    def linear_search(self, product_list, search):
        results = []
        search = search.lower()
        for product in product_list:
            product_name = product['product_name']
            category_name = product['product_name']
            if product_name and search in product_name.lower():
             results.append(product)
            elif category_name and search in category_name.lower():
             results.append(product)

        return results

    # Cache inventory results for faster access
    @cache_result(timeout=120, key_prefix='inventory_list')
    def get(self, request, format=None):
        user_id = request.user.id
        search = request.GET.get('search')
        
        @cache_result(timeout=300, key_prefix=f'store_manager_{user_id}')
        def get_store_manager():
            return AssignStoreManagers.objects.filter(user_id=user_id).first()
            
        fulfillment_manager = get_store_manager()

        if not fulfillment_manager:
            return Response({'status': False, 'data': {}, 'msg': 'Store manager not found'}, status=status.HTTP_200_OK)

        store_id = fulfillment_manager.store_id
        
        # Use cache_queryset to efficiently cache complex query results
        @cache_result(timeout=180, key_prefix="inventory_products")
        def get_inventory_products():
            return StoreInventory.objects.filter(store_id=store_id, status=1).select_related(
                'product__category'
            ).only(
                'product_id', 'inventory', 'updated_at'
            ).order_by('-updated_at').values(
                'product_id',
                'inventory',
                'store_id',
                updated_date=F('updated_at'),
                stock=F('inventory'),
                product_name=F('product__product_name'),
                category_id=F('product__category_id'),
                category_name=F('product__category__name'),
            )
            
        product_list = get_inventory_products()

        if search:
            search = search.lower()
            search_index = self.binary_search(product_list, search)

            if search_index != -1:
                return Response({'status': True, 'data': [product_list[search_index]], 'msg': 'Store product listing'},
                                status=status.HTTP_200_OK)
            else:
                partial_matches = self.linear_search(product_list, search)
                if partial_matches:
                    return Response({'status': True, 'data': partial_matches, 'msg': 'Store product listing'},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({'status': False, 'data': [], 'msg': 'Product not found'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': True, 'data': product_list, 'msg': 'Store product listing'}, status=status.HTTP_200_OK)

class Notifications(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        user_id = request.user.id
        notifications = Notification.objects.filter(user_id=user_id)
        if notifications.exists():

            notification_list = Notification.objects.filter(user_id = user_id)
            listnotification = NotificationListSerializer(notification_list, many=True).data
            return Response({'status':True, 'data': listnotification,'msg': 'Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'status':False, 'data': [],'msg': 'Data not found'}, status=status.HTTP_200_OK)


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        device_id = request.data.get('device_id')
        user_id = request.user.id
        delete = FcmToken.objects.filter(device_id=device_id, user_id=user_id).delete()
        
        # Invalidate all user-related caches
        invalidate_cache_pattern(f'is_storemanager_{user_id}')
        invalidate_cache_pattern(f'store_manager_{user_id}')
        invalidate_cache_pattern(f'fcm_token_{user_id}')
        
        logout(request)
        return Response({'status':True, 'data': {},'msg': 'Successfully Logged Out'}, status=status.HTTP_200_OK)

