import requests
import base64
import urllib.parse
import http.cookiejar as cookielib
import os
import json
import websocket
websocket.enableTrace(False)
import threading
from data.db import Database


class VRChatAPI:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VRChatAPI, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    BASE_URL = "https://api.vrchat.cloud/api/1"
    WS_URL = "wss://pipeline.vrchat.cloud/"

    def __init__(self):
        if self._initialized:
            return
        
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "VRCRM/1.0 (ciavatarsvr@gmail.com)"
        })
        self.cookie_file = os.path.join(os.path.dirname(__file__), 'cookies.txt')

        self.session.cookies = cookielib.LWPCookieJar(self.cookie_file)
        self._load_cookies()
        self._initialized = True

    def _load_cookies(self):
        if os.path.exists(self.cookie_file):
            try:
                self.session.cookies.load(ignore_discard=True)
            except Exception:
                pass

    def _save_cookies(self):
        self.session.cookies.save(ignore_discard=True)
    
    def _build_auth_header(self, username, password):
        user = urllib.parse.quote(username)
        pwd = urllib.parse.quote(password)
        token = base64.b64encode(f"{user}:{pwd}".encode("utf-8")).decode("utf-8")
        return {"Authorization": f"Basic {token}"}
    
    def is_logged_in(self):
        url = f"{self.BASE_URL}/auth/user"
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            self.user_id = data.get("id")
            return True, data
        return False, None
    
    def get_user_id(self):
        return self.user_id

    def login(self, username, password, totp_code=None):
        logged_in, user_data = self.is_logged_in()
        if logged_in:
            return user_data

        if totp_code:
            # Si ya tenemos el código TOTP, completamos el flujo 2FA directamente
            return self._complete_totp(totp_code)
        
        headers = self._build_auth_header(username, password)
        url = f"{self.BASE_URL}/auth/user"
        response = self.session.get(url, headers=headers)

        if response.status_code == 200:
            self._save_cookies()
            data = response.json()
            self.user_id = data.get("id")
            return data
        
        # if TOTP needed

        if response.status_code == 401:
            data = response.json().get("requiresTwoFactorAuth")
            if data:
                if not totp_code:
                    return {"requiresTwoFactorAuth": data}
        
        raise Exception(f"Login failed: {response.status_code} {response.text}")
    
    def _complete_totp(self, totp_code):
        url = f"{self.BASE_URL}/auth/twofactorauth/totp/verify"
        payload = {"code": totp_code}
        headers = {"Content-Type": "application/json"}

        response = self.session.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            self._save_cookies()
            user_url = f"{self.BASE_URL}/auth/user"
            user_response = self.session.get(user_url)
            
            if response.status_code == 200:
                self._save_cookies()
                data = response.json()
                self.user_id = data.get("id")
                return data
            else:
                raise Exception(f"Error getting user: {user_response.status_code} {user_response.text}")
        raise Exception(f"TOTP failed: {response.status_code} {response.text}")

    def get_user_by_id(self, user_id):
        url = f"{self.BASE_URL}/users/{user_id}"
        response = self.session.get(url)

        if response.status_code != 200:
            raise Exception(f"Failed to get user id: {response.status_code} {response.text}")
        
        return response.json()

    
    def connect_pipeline(self, auth_token=None, on_event=None):
        token = auth_token or self._extract_auth_from_cookies()
        url = f"{self.WS_URL}?authToken={token}"

        def _on_message(ws, msg):
            outer = json.loads(msg)
            content = outer.get("content")
            try:
                parsed = json.loads(content) if isinstance(content, str) else content
            except:
                parsed = content
            
            event_type = outer.get("type")
            event = {"type": event_type, "content": parsed}
            
            db = None

            if event_type in ["notification", "response-notification", "notification-v2"]:
                db = Database()
                print(f"meow notif {event_type}")
                user_id = None
                message = None
                
                if event_type == "notification":
                    user_id = parsed.get("senderUserId") or parsed.get("reciverUserId")
                    # Si el mensaje es un diccionario o contenido complejo, guardarlo tal cual
                    message = parsed
                elif event_type == "response-notification":
                    user_id = parsed.get("receiverId")
                    message = f"Response to notification {parsed.get('notificationId')}"
                elif event_type == "notification-v2":
                    user_id = parsed.get("senderUserId") or parsed.get("receiverUserId")
                    # Si el mensaje es un diccionario o contenido complejo, guardarlo tal cual
                    message = parsed
                
                if user_id:
                    db.insert_log(user_id, invitation_type=event_type, message=message)
                
                if db:
                    db.close()

            if on_event:
                on_event(event)

        headers = [
            "User-Agent: VRCRM/1.0 (ciavatarsvr@gmail.com)"
        ]                    

        ws = websocket.WebSocketApp(url, header=headers,  on_message=_on_message)
        t = threading.Thread(target=ws.run_forever, kwargs={"ping_interval": 30})
        t.daemon = True
        t.start()
        self._ws = ws
    
    def _extract_auth_from_cookies(self):
        for c in self.session.cookies:
            if c.name == "auth":
                return c.value.strip('"') # type: ignore
        
        raise Exception("Auth token not found in cookies")
    
    #region invite
    def get_all_vrchat_messages(self, user_id, message_type="message"):
        url = f"{self.BASE_URL}/message/{user_id}/{message_type}"
        response = self.session.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch messages: {response.status_code} {response.text}")
        
        return response.json()
    
    def send_invite_response(self, notification_id, slot):
        url = f"{self.BASE_URL}/invite/{notification_id}/response"
        payload = {"responseSlot": slot}
        headers = {"Content-Type": "application/json"}

        response = self.session.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to send invite response: {response.status_code} {response.text}")
    
    def send_invite(self, target_user_id, slot):
        url = f"{self.BASE_URL}/invite/{target_user_id}"
        payload = {"messageSlot": slot}
        headers = {"Content-Type": "application/json"}

        response = self.session.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to send invite: {response.status_code} {response.text}")


