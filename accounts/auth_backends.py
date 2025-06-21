# from django.contrib.auth.backends import ModelBackend
# from django.contrib.auth import get_user_model
# from django.core.cache import cache
# from django.conf import settings
# from datetime import timedelta
# from django.utils import timezone

# class LockoutBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         # Increment the failed login attempts count
#         cache_key = f'login_attempts_{username}'
#         attempts = cache.get(cache_key, 0)
#         print("Current attempts:", attempts)
#         attempts += 1
#         cache.set(cache_key, attempts, settings.LOGIN_ATTEMPTS_TIMEOUT)

#         user = super().authenticate(request, username, password, **kwargs)
#         print("555555555555", user, settings.MAX_LOGIN_ATTEMPTS)

#         # Lock the account if the maximum attempts are reached
#         if attempts >= settings.MAX_LOGIN_ATTEMPTS:
#             print(attempts, "8888888888888")
#             try:
#                 print("9999999977", username)
#                 user_to_lock = get_user_model().objects.get(mobile=username)
#                 print("9999999977", user_to_lock.is_active)

#                 # Check if the user is not already locked
#                 current_time = timezone.now()
#                 lockout_duration = timedelta(seconds=30)
#                 user_to_lock.locked_until = current_time + lockout_duration
#                 if user_to_lock.is_active:
#                     print("mmm")
#                     # Set the account to be locked for 30 seconds
#                     user_to_lock.is_active = False
#                     print("77777888888888888", user_to_lock.locked_until)
#                     user_to_lock.save()

#                 # Check if it's time to reset is_active
#                 if not user_to_lock.is_active and current_time >= user_to_lock.locked_until:
#                     user_to_lock.is_active = True
#                     user_to_lock.save()
#                     cache.delete(cache_key)  # Reset the failed login attempts count

#             except get_user_model().DoesNotExist:
#                 print("hnjjj")
#                 # Handle the case when the user does not exist
#                 pass

#         return user
