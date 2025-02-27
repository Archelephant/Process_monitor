import os
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import time

def get_random_chrome_user_agent():
    user_agent = UserAgent(browsers='chrome', os='windows', platforms='pc')
    return user_agent.random

#Инициация драйвера
#Не забудьте создать папку users в корне вашего проекта!

def create_driver(user_id=1):
    options = Options()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_directory = os.path.join(script_dir, 'users')
    user_directory = os.path.join(base_directory, f'user_{user_id}')

    options.add_argument(f'user-data-dir={user_directory}')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument('--no-sandbox')
    # options.add_argument('--headless')

    driver = webdriver.Chrome(options=options)
    ua = get_random_chrome_user_agent()
    stealth(driver=driver,
            user_agent=ua,
            languages=["ru-RU", "ru"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            run_on_insecure_origins=True
            )

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
      '''
    })
    return driver

def main_login(user_id=1):
    driver = create_driver(user_id)
    driver.get('Ccылка на любой сайт)
    time.sleep(350)

# Получаем имя интерфейса Wi-Fi
for interface in interfaces()
wifi_interface = next(interface for interface in interfaces() if 'wlan' in interface)

#TO DO: add main function