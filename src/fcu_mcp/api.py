import json

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .logger import logger


class ILearnAPI:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
    
    def login(self, username: str, password: str):
        self.driver.get('https://ilearn.fcu.edu.tw/login/index.php')
        self.driver.find_element(By.ID, 'username').send_keys(username)
        self.driver.find_element(By.ID, 'password').send_keys(password)
        self.driver.find_element(By.ID, 'loginbtn').click()
        
        # cache html
        with open('ilearn.html', 'w', encoding='utf-8') as f:
            f.write(self.driver.page_source)
        
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'logininfo')))
            return True
        except:
            return False
    
    def get_future_events(self):
        self.driver.get('https://ilearn.fcu.edu.tw/my/')
        try:
            future_events_container = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, 'inst1102471'))
            )
            
            event_elements = future_events_container.find_elements(By.CLASS_NAME, 'event')
            future_events = []
            for event in event_elements:
                future_events.append({
                    'title': event.find_element(By.CLASS_NAME, 'text-truncate').text,
                    'link': event.find_element(By.CLASS_NAME, 'text-truncate').get_attribute('href'),
                    'date': event.find_element(By.CLASS_NAME, 'date').text,
                })
            return future_events
        except TimeoutException:
            raise TimeoutException('Timeout while waiting for future events')
        except Exception as e:
            logger.error(f'Error while fetching future events: {e}')
            return []

class MyFcuAPI:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
    
    def login(self, username: str, password: str) -> bool:
        self.driver.get('https://myfcu.fcu.edu.tw/main/infomyfculogin.aspx')
        self.driver.find_element(By.ID, 'txtUserName').send_keys(username)
        self.driver.find_element(By.ID, 'txtPassword').send_keys(password)
        self.driver.find_element(By.ID, 'OKButton').click()
        
        try:
            cookies = self.driver.get_cookies()
            cookie_keys = {cookie['name'] for cookie in cookies}
            required_keys = {'ASP.NET_SessionId'}
            return required_keys.issubset(cookie_keys)
        except WebDriverException:
            return False
    
    def get_course_list(self, year: int, smester: int) -> list[dict]:
        url = 'https://myfcu.fcu.edu.tw/main/S3202/S3202_timetable_new.aspx/GetLineCourseList'
        payload = {
            'year': year,
            'smester': smester,
        }
        
        try:
            self.driver.get(url)
            script = f"""
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "{url}", false);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(JSON.stringify({json.dumps(payload)}));
            return xhr.responseText;
            """
            
            response_text = self.driver.execute_script(script)
            response_data = json.loads(response_text)
            return response_data.get('d', [])
        except Exception as e:
            logger.error(f'Error while fetching course list using WebDriver: {e}')
            raise e