from data.db import Database
class Notification:
    _instance = None
    _initialized = False

    def __new__(cls,*args, **kwargs):
        if not cls._instance:
            cls._instance = super(Notification, cls).__new__(cls,*args, **kwargs)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.db = Database()
    
    def insert_notification_to_db(self, notification):
        
        notification_info = self.get_info_from_notification(notification)
        
        user_id = notification_info.get("user_id")
        noti_type = notification_info.get("type")
        date_notification = notification_info.get("date")
        message_notification = notification_info.get("message")
        
        self.db.insert_log(user_id, noti_type, date_notification, message_notification)
    
    def get_info_from_notification(self, notification):
        sender_user_id = notification.get("senderUserId")
        sender_user_name = notification.get("senderUsername")
        notification_type = notification.get("type")
        details = notification.get("details", {})
        date = notification.get("created_at").replace("Z", "")

        message = None
        match notification_type:
            case "invite":
                message = details.get("inviteMessage", "")
            case "requestInvite":
                message = details.get("requestMessage", "")
            case "inviteResponse":
                message = details.get("responseMessage", "")
        
        return {
            "user_id": sender_user_id,
            "username": sender_user_name,
            "type": notification_type,
            "date": date,
            "message": message
        }
        

            

        