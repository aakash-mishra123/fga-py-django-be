from django.urls import path
from storemanager.views import LoginView,Notifications,InventoryListnew,NewOrderList,StoreBoyProfile,LogoutView,StoreDetails,StoreAttendance,MyTeamList,InventoryList,OrderListAll,SendPasswordResetEmailView,StoreManagerBoyView,DashboardView,OrderDetailsView

urlpatterns = [
    path('login/', LoginView.as_view(), name="storemanager-login"), 
    path('forgot-password-email/', SendPasswordResetEmailView.as_view(), name="storemanager-resetpasssword-email"),
    path('profile/', StoreManagerBoyView.as_view(), name="storemanager-profile"),   
    path('dashboard/', DashboardView.as_view(), name="dashboard"),
    path('order_details/', OrderDetailsView.as_view(), name="dashboard"),
    path('new_order_list/', NewOrderList.as_view(), name="new_order_list"),
    path('order_list/', OrderListAll.as_view(), name="order_list"),
    path('inventory_list/', InventoryList.as_view(), name="inventory_list"),
    path('inventory_listnew/', InventoryListnew.as_view(), name="inventory_listnew"),
    path('my_team/', MyTeamList.as_view(), name="my_team"),
    path('storeboy_attendance/', StoreAttendance.as_view(), name="storeboy_attendance"),
    path('storeboy_details/', StoreDetails.as_view(), name="storeboy_details"),
    path('storeboy_profile/', StoreBoyProfile.as_view(), name="storeboy_profile"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('notifications/', Notifications.as_view(), name="notifications"),
]