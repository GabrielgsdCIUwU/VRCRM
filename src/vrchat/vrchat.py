import requests
import base64
import urllib.parse
import http.cookiejar as cookielib
import os


class VRChatAPI:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VRChatAPI, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    BASE_URL = "https://api.vrchat.cloud/api/1"

    def __init__(self):
        if self._initialized:
            return

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
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    
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
            return response.json()
        
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
            
            if user_response.status_code == 200:
                return user_response.json()
            else:
                raise Exception(f"Error getting user: {user_response.status_code} {user_response.text}")
        raise Exception(f"TOTP failed: {response.status_code} {response.text}")
            
