import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

class FirebaseMessaging:
    def __init__(self):
        # Path to your service account JSON file
        self.credentials_path = 'path/to/your-service-account.json'
        self.project_id = 'myproject-b5ae1'  # Replace with your project ID
        
        # FCM v1 endpoint
        self.base_url = f'https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send'
        
        # Initialize credentials
        self.credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=['https://www.googleapis.com/auth/firebase.messaging']
        )
        
    def get_access_token(self):
        """Get authorized session for making requests"""
        return AuthorizedSession(self.credentials)
        
    def send_message(self, registration_token, title, body, data=None):
        """Send FCM message using HTTP v1 API"""
        
        # Message payload
        message = {
            'message': {
                'token': registration_token,
                'notification': {
                    'title': title,
                    'body': body
                },
                'android': {
                    'notification': {
                        'click_action': 'FLUTTER_NOTIFICATION_CLICK',
                        'sound': 'default'
                    }
                },
                'apns': {
                    'payload': {
                        'aps': {
                            'sound': 'default'
                        }
                    }
                }
            }
        }
        
        # Add additional data if provided
        if data:
            message['message']['data'] = data
            
        # Get authorized session
        authed_session = self.get_access_token()
        
        # Send request
        response = authed_session.post(
            url=self.base_url,
            json=message
        )
        
        return response.json()