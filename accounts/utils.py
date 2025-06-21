from django.core.mail import EmailMessage
import os
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.core.cache import cache
from accounts.cache_utils import cache_with_prefix, invalidate_cache_pattern, invalidate_prefix
import logging

from django.shortcuts import render
from django.conf import settings

logger = logging.getLogger(__name__)

class Util:
  @staticmethod
  def send_email(data):
    email = EmailMessage(
      subject=data['subject'],
      body=data['body'],
      from_email=os.environ.get('EMAIL_FROM'),
      to=[data['to_email']]
    )
    email.send()

class CachedUtil:
  @staticmethod
  def get_cached_user_data(user_id, timeout=300):
    """
    Get cached user data or fetch and cache if not available
    """
    cache_key = f"user_data_{user_id}"
    user_data = cache.get(cache_key)
    
    if user_data is None:
      from accounts.models import User
      try:
        user = User.objects.get(id=user_id)
        from accounts.serializers import UserFullProfileSerializer
        serializer = UserFullProfileSerializer(user)
        user_data = serializer.data
        cache.set(cache_key, user_data, timeout)
      except User.DoesNotExist:
        return None
        
    return user_data
    
  @staticmethod
  def cache_user_batch_data(users_dict, timeout=300):
    """
    Cache multiple users' data at once
    """
    try:
      cache_with_prefix("users_batch", users_dict, timeout)
      logger.debug(f"Cached batch data for {len(users_dict)} users")
    except Exception as e:
      logger.error(f"Error caching user batch data: {str(e)}")
      
  @staticmethod
  def invalidate_user_data(user_id):
    """
    Invalidate all caches related to a user
    """
    try:
      invalidate_prefix(f"user_{user_id}")
      invalidate_cache_pattern(f"user_{user_id}")
      logger.debug(f"Invalidated all cache data for user {user_id}")
    except Exception as e:
      logger.error(f"Error invalidating user cache data: {str(e)}")


# from axes.models import AccessAttempt
# from django.utils import timezone

# def reset_login_attempts(user):
#     # Reset login attempts in the django-axes table
#     AccessAttempt.objects.filter(username=user.username).delete()

#     # Reset any custom failed login attempt tracking in your user model (if applicable)
#     user.failed_login_attempts = 0
#     user.save()



# def reset_lockout(user):
#     # Check if the user is currently locked out
#     if AccessAttempt.objects.is_blocked(username=user.username):
#         # Reset lockout by setting the last login attempt to a past time
#         AccessAttempt.objects.update(username=user.username, failures_since_start=0, attempts=0, last_attempt=timezone.now() - timezone.timedelta(minutes=5))

#         # Alternatively, you can delete the lockout entry
#         # AccessAttempt.objects.filter(username=user.username).delete()

#     # Reset any custom lockout tracking in your user model (if applicable)
#     user.is_locked = False
#     user.save()


def some_protected_view(request):
    if request.session.session_key != request.COOKIES.get('sessionid'):
        # Session ID mismatch, log the user out
        logout(request)
        return redirect('login')
