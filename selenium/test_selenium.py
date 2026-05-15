from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def create_driver():
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )


# ================= LOGIN =================

def test_admin_login():

    driver = create_driver()

    driver.get("http://127.0.0.1:5000/login")

    time.sleep(1)

    driver.find_element(By.NAME, "username").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("123")

    driver.find_element(By.TAG_NAME, "button").click()

    time.sleep(2)

    assert "Admin" in driver.page_source

    driver.quit()


# ================= RESERVATION =================

def test_reservation_success():

    driver = create_driver()

    driver.get("http://127.0.0.1:5000/reserve")

    time.sleep(1)

    driver.find_element(By.NAME, "name").send_keys("duy")
    driver.find_element(By.NAME, "email").send_keys("duy1@gmail.com")
    driver.find_element(By.NAME, "phone").send_keys("0823656989")
    driver.find_element(By.NAME, "guests").send_keys("6")

    date_input = driver.find_element(By.NAME, "date")

    driver.execute_script(
        "arguments[0].value = '2026-12-24';",
        date_input
    )

    time_input = driver.find_element(By.NAME, "time")

    driver.execute_script(
        "arguments[0].value = '18:00';",
        time_input
    )

    driver.find_element(By.NAME, "table_number").send_keys("7")

    driver.find_element(By.TAG_NAME, "button").click()

    time.sleep(2)

    assert "Đặt bàn thành công" in driver.page_source

    driver.quit()


# ================= ADD MENU =================

def test_add_menu():

    driver = create_driver()

    driver.get("http://127.0.0.1:5000/login")

    time.sleep(1)

    driver.find_element(By.NAME, "username").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("123")

    driver.find_element(By.TAG_NAME, "button").click()

    time.sleep(2)

    driver.get("http://127.0.0.1:5000/admin/menu/add")

    time.sleep(1)

    driver.find_element(By.NAME, "name").send_keys("Pizza Selenium")
    driver.find_element(By.NAME, "price").send_keys("120")
    driver.find_element(By.NAME, "description").send_keys("Ngon")

    image_input = driver.find_element(By.NAME, "image")
    image_input.send_keys(r"D:\restaurant_booking\static\test.jpg")

    driver.find_element(By.TAG_NAME, "button").click()

    time.sleep(2)

    assert "Pizza Selenium" in driver.page_source

    driver.quit()

  # ================= INVALID TIME =================

def test_reservation_invalid_time():
        driver = create_driver()

        driver.get("http://127.0.0.1:5000/reserve")

        time.sleep(1)

        driver.find_element(By.NAME, "name").send_keys("phuc")
        driver.find_element(By.NAME, "email").send_keys("phuc@gmail.com")
        driver.find_element(By.NAME, "phone").send_keys("0183456789")
        driver.find_element(By.NAME, "guests").send_keys("7")

        date_input = driver.find_element(By.NAME, "date")

        driver.execute_script(
            "arguments[0].value = '2026-12-23';",
            date_input
        )

        # giờ sai
        time_input = driver.find_element(By.NAME, "time")

        driver.execute_script(
            "arguments[0].value = '11:00';",
            time_input
        )

        driver.find_element(By.NAME, "table_number").send_keys("2")

        driver.find_element(By.TAG_NAME, "button").click()

        time.sleep(2)

        assert "Đặt bàn không thành công" in driver.page_source

        driver.quit()