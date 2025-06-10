import tempfile
import threading
from typing import Dict

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class UserDriverManager:
    def __init__(self):
        self._drivers: Dict[str, webdriver.Chrome] = {}
        self._lock = threading.Lock()
    
    def get_driver(self, user_id: str) -> webdriver.Chrome:
        with self._lock:
            if user_id not in self._drivers:
                self._drivers[user_id] = self._create_driver()
            return self._drivers[user_id]
    
    def _create_driver(self) -> webdriver.Chrome:
        options = Options()
        temp_dir = tempfile.mkdtemp()
        options.add_argument('--headless')  # 無界面模式
        options.add_argument(f'--user-data-dir={temp_dir}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=options)
        return driver
    
    def is_ilearn_logged_in(self, user_id: str) -> bool:
        with self._lock:
            if user_id in self._drivers:
                driver = self._drivers[user_id]
                driver.get('https://ilearn.fcu.edu.tw/')
                try:
                    logininfo_element = driver.find_element(By.CLASS_NAME, 'logininfo')
                    return True
                except Exception as e:
                    print(f"Error checking iLearn login status for user {user_id}: {e}")
                    return False
            return False
    
    def is_myfcu_logged_in(self, user_id: str) -> bool:
        with self._lock:
            if user_id in self._drivers:
                driver = self._drivers[user_id]
                driver.get('https://myfcu.fcu.edu.tw/')
                try:
                    cookies = driver.get_cookies()
                    cookie_keys = {cookie['name'] for cookie in cookies}
                    required_keys = {'ASP.NET_SessionId'}
                    return required_keys.issubset(cookie_keys)
                except WebDriverException:
                    return False
            return False
    
    def have_driver(self, user_id: str) -> bool:
        with self._lock:
            return user_id in self._drivers
    
    def close_driver(self, user_id: str):
        with self._lock:
            if user_id in self._drivers:
                self._drivers[user_id].quit()
                del self._drivers[user_id]
    
    def close_all_drivers(self):
        with self._lock:
            for driver in self._drivers.values():
                driver.quit()
            self._drivers.clear()