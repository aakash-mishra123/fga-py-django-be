from accounts.models import User
from stores.models import Stores
from product.models import Order, Product
from .cache_utils import cache_result
import logging

logger = logging.getLogger(__name__)

# Cache key prefixes
USER_BY_MOBILE_CACHE_PREFIX = "user_by_mobile"
STORE_DETAIL_CACHE_PREFIX = "store_detail"
STORE_ORDERS_CACHE_PREFIX = "store_orders"
STORE_PRODUCTS_CACHE_PREFIX = "store_products" # Assuming products might be store-specific

def is_storemanager_role(user): # Renamed from is_storemanager to avoid conflict if imported directly
    return user.groups.filter(name='storemanager').exists()

@cache_result(timeout=60 * 10, key_prefix=USER_BY_MOBILE_CACHE_PREFIX) # Cache for 10 minutes
def get_user_by_mobile(mobile: str):
    """
    Fetches a user by mobile.
    Cache key: "user_by_mobile:<mobile>"
    """
    logger.info(f"DB: Fetching user by mobile={mobile}")
    try:
        return User.objects.get(mobile=mobile)
    except User.DoesNotExist:
        return None

@cache_result(timeout=60 * 15, key_prefix=STORE_DETAIL_CACHE_PREFIX) # Cache for 15 minutes
def get_store_details(store_id: int):
    """
    Fetches store details by ID.
    Cache key: "store_detail:<store_id>"
    """
    logger.info(f"DB: Fetching store details for store_id={store_id}")
    try:
        return Stores.objects.get(id=store_id)
    except Stores.DoesNotExist:
        return None

@cache_result(timeout=60 * 5, key_prefix=STORE_ORDERS_CACHE_PREFIX) # Cache for 5 minutes
def get_orders_for_store(store_id: int, status: str = None):
    """
    Fetches orders related to a specific store, optionally filtered by status.
    Cache key: "store_orders:<store_id>:status:<status>" or "store_orders:<store_id>"
    """
    logger.info(f"DB: Fetching orders for store_id={store_id}, status={status}")
    # This query assumes a relationship like Order.store_id or similar.
    # Adjust the filter based on your actual models.
    # For example, if orders are linked via an assigned store or delivery boy's store.
    # Placeholder: Order.objects.filter(assigned_store_id=store_id)
    queryset = Order.objects.filter(store_id=store_id) # Assuming Order has a direct store_id FK
    if status:
        queryset = queryset.filter(status=status)
    return list(queryset.order_by('-created_at'))


@cache_result(timeout=60 * 30, key_prefix=STORE_PRODUCTS_CACHE_PREFIX) # Cache for 30 minutes
def get_products_for_store(store_id: int):
    """
    Fetches products available or managed by a specific store.
    Cache key: "store_products:<store_id>"
    """
    logger.info(f"DB: Fetching products for store_id={store_id}")
    # This query assumes products are related to stores. Adjust as per your model structure.
    # Example: Product.objects.filter(store_id=store_id) or Product.objects.filter(availability__store_id=store_id)
    return list(Product.objects.filter(store_id=store_id)) # Assuming Product has a direct store_id FK
