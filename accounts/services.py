from .models import User, UserActivity
from .cache_utils import cache_result, invalidate_prefix, get_cached_or_set

class UserService:
    # ...existing code...
    
    @cache_result(timeout=600, key_prefix="user_activity")
    def get_user_activity(self, user_id):
        """
        Fetches user activity data for a given user.
        
        Args:
            user_id: ID of the user whose activity data is to be fetched
            
        Returns:
            List of user activity records
        """
        activities = UserActivity.objects.filter(user_id=user_id)
        return activities
    
    def get_user_permissions(self, user_id):
        """
        Retrieve cached permissions for a user, or compute and cache them if not available.
        
        Args:
            user_id: ID of the user whose permissions are to be fetched
            
        Returns:
            Dictionary of user permissions
        """
        # Cache all permissions with a common prefix
        def fetch_permissions():
            permissions = {}
            # ...code to fetch permissions...
            return permissions
            
        return get_cached_or_set(
            f"user_permissions:{user_id}",
            fetch_permissions,
            timeout=1800
        )
    
    def update_user_permissions(self, user_id, new_permissions):
        """
        Update the permissions for a user and invalidate the cache.
        
        Args:
            user_id: ID of the user whose permissions are to be updated
            new_permissions: Dictionary of new permissions to be set
            
        Returns:
            None
        """
        # Update permissions
        # ...existing code...
        # Invalidate cache
        invalidate_prefix(f"user_permissions:{user_id}")