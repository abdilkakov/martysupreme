import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ------------------------------
# Конфигурация
# ------------------------------
USERNAME = "z_abdilkakov"
PASSWORD = "Jasikbr1234567890"
TELEGRAM_BOT_TOKEN = "7930510036:AAFrnsu_eAeqtvzfl9q3CxQl4EJrkRRufGQ"
TELEGRAM_CHAT_ID = "6855224263"
REFRESH_INTERVAL = 20  # секунд
LOGIN_URL = "https://wsp.kbtu.kz/RegistrationOnline"
KEEP_BROWSER_OPEN = True  # оставить браузер открытым после ошибки
# ------------------------------


def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        return False


def do_login(driver, wait):
    print("Attempting login...")
    driver.get(LOGIN_URL)
    time.sleep(2)

    # Username combobox
    username_field = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//input[contains(@class, 'v-filterselect-input')]")
    ))
    username_field.clear()
    username_field.send_keys(USERNAME)
    time.sleep(0.5)
    username_field.send_keys(Keys.ENTER)

    # Password field
    password_field = driver.find_element(By.XPATH, "//input[@type='password']")
    password_field.clear()
    password_field.send_keys(PASSWORD)

    # Login button
    login_button = driver.find_element(By.XPATH, "//div[contains(@class, 'v-button') and contains(@class, 'primary')]")
    login_button.click()
    print("Clicked login button")
    time.sleep(5)

    driver.save_screenshot("/tmp/login_result.png")
    print("Screenshot saved to /tmp/login_result.png")
    print(f"After login URL: {driver.current_url}")

    send_telegram_message(f"Logged in. Current URL: {driver.current_url}")


def is_session_expired(driver):
    try:
        buttons = driver.find_elements(By.XPATH, "//span[@class='v-button-caption']") or []
        for btn in buttons:
            if btn.text in ['Кіру', 'Войти', 'Login']:
                return True
        login_fields = driver.find_elements(By.XPATH, "//input[@type='password']") or []
        return bool(login_fields)
    except:
        return True


def main():
    print("Starting...")
    options = Options()
    options.add_argument("--ignore-certificate-errors")
    # options.add_argument("--headless")  # отключено для видимого браузера
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)

    try:
        do_login(driver, wait)
        refresh_count = 0

        while True:
            refresh_count += 1
            print(f"\n[{time.strftime('%H:%M:%S')}] Refresh #{refresh_count}")

            driver.get(LOGIN_URL)
            time.sleep(3)

            # Проверяем сессию
            if is_session_expired(driver):
                print(">>> Session expired! Re-logging in...")
                do_login(driver, wait)
                time.sleep(5)

            # Ищем кнопку "Отметиться"
            try:
                otmetitsya_button = driver.find_elements(
                    By.XPATH,
                    "//span[@class='v-button-caption' and text()='Отметиться']/ancestor::div[contains(@class, 'v-button')]"
                ) or []

                if otmetitsya_button:
                    clicked = False
                    for btn in otmetitsya_button:
                        if btn.is_displayed() and btn.is_enabled():
                            btn.click()
                            print(">>> CLICKED 'Отметиться' <<<")
                            send_telegram_message(f"Refresh #{refresh_count}: ATTENDANCE MARKED ✅")
                            clicked = True
                            break
                    if not clicked:
                        print("Button 'Отметиться' found but not clickable")
                        send_telegram_message(f"Refresh #{refresh_count}: Button 'Отметиться' found but not clickable ⚠️")
                else:
                    print("Button 'Отметиться' not available")
                    send_telegram_message(f"Refresh #{refresh_count}: Button 'Отметиться' not found ❌")

            except Exception as e:
                print(f"Error clicking 'Отметиться': {e}")
                send_telegram_message(f"Refresh #{refresh_count}: Error clicking 'Отметиться': {e}")

            print(f"Waiting {REFRESH_INTERVAL} seconds...")
            time.sleep(REFRESH_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopped by user")
        send_telegram_message("Script stopped by user ✋")
    except Exception as e:
        print(f"Error: {e}")
        send_telegram_message(f"Script error: {e}")
    finally:
        if not KEEP_BROWSER_OPEN:
            driver.quit()
            print("Browser closed")
        else:
            print("Browser left open for debugging")


if __name__ == "__main__":
    main()
