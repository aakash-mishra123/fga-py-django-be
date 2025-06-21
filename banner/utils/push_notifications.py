from pyfcm import FCMNotification

def send_push_notification(title, message, registration_ids, server_key):
    push_service = FCMNotification(api_key=server_key)

    data_message = {
        "title": title,
        "body": message,
    }

    result = push_service.notify_multiple_devices(
        registration_ids=registration_ids,
        data_message=data_message,
    )

    return result