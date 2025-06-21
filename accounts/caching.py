from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class UserCacheMixin:
    """Mixin for caching user related queries to reduce database load"""
    
    @staticmethod
    def get_user_by_username(username, include_inactive=False):
        """Get a user by username with caching to improve form performance"""
        cache_key = f"user_by_name_{username}{'_all' if include_inactive else ''}"
        user = cache.get(cache_key)
        
        if user is None:
            query = UserModel._default_manager.filter(username__iexact=username)
            if not include_inactive:
                query = query.filter(is_active=True)
                
            try:
                # Use select_related to include related profile data in one query
                if hasattr(UserModel, 'profile'):
                    user = query.select_related('profile').get()
                else:
                    user = query.get()
                    
                # Cache for a short time to prevent stale data
                cache.set(cache_key, user, timeout=settings.FORM_CACHE_TIMEOUT 
                          if hasattr(settings, 'FORM_CACHE_TIMEOUT') else 60)
            except UserModel.DoesNotExist:
                # Cache negative lookups too, but for less time
                cache.set(cache_key, None, timeout=30)
                user = None
                
        return user
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get a user by ID with caching"""
        cache_key = f"user_by_id_{user_id}"
        user = cache.get(cache_key)
        
        if user is None:
            try:
                if hasattr(UserModel, 'profile'):
                    user = UserModel._default_manager.select_related('profile').get(pk=user_id)
                else:
                    user = UserModel._default_manager.get(pk=user_id)
                cache.set(cache_key, user, timeout=settings.FORM_CACHE_TIMEOUT 
                          if hasattr(settings, 'FORM_CACHE_TIMEOUT') else 60)
            except UserModel.DoesNotExist:
                cache.set(cache_key, None, timeout=30)
                user = None
                
        return user
        
    @staticmethod
    def clear_user_cache(username=None, user_id=None):
        """Clear cached user data when user is updated"""
        if username:
            cache.delete(f"user_by_name_{username}")
            cache.delete(f"user_by_name_{username}_all")
        if user_id:
            cache.delete(f"user_by_id_{user_id}")