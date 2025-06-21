from django.urls import path
from .import views
from fidelity.views import getorderstatusview,createorderView,getupgradeprimeorderinformation,getorderinformation,JoinPrimeView,getprimeorderinformation,UpgradePrimePlanView

from django.urls import path, include

urlpatterns = [
    path('create_order/',createorderView.as_view(), name='createorderView'),
    path('join_prime/',JoinPrimeView.as_view(), name='join_prime'),
    path('upgrade_prime_plan/',UpgradePrimePlanView.as_view(), name='upgrade_prime_plan'),
    #  path('get-products/', GetProductView.as_view(), name="get-products"),
    path('get_order_status/', getorderstatusview.as_view(), name='get_order_status'),
    path('get_order_information/', getorderinformation.as_view(), name='get_order_status'),
    path('get_prime_order_information/', getprimeorderinformation.as_view(), name='get_prime_order_information'),
    path('get_upgrade_prime_order_information/', getupgradeprimeorderinformation.as_view(), name='get_upgrade_prime_order_information'),
    # Add more URL patterns as needed
]