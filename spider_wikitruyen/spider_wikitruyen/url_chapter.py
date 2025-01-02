import re
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Cấu hình Chrome để theo dõi các yêu cầu mạng
# caps = DesiredCapabilities.CHROME
# caps["goog:loggingPrefs"] = {"performance": "ALL"}

# Đọc danh sách URL từ file JSON
current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "links.json")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
web = data["urls"][0]  # Gắn vào 

# Đường dẫn tới ChromeDriver
path = 'D:\\Backup\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe'

# Cấu hình ChromeOptions
option = Options()
option.add_argument("--window-size=1920,1200")
option.set_capability("goog:loggingPrefs", {"performance": "ALL"})

# Sử dụng Service để quản lý ChromeDriver
service = Service(path)
driver = webdriver.Chrome(service=service, options=option)

# Bật Network logging bằng DevTools Protocol
driver.execute_cdp_cmd("Network.enable", {})

# Truy cập trang web
# web = "https://truyenwikidich.net/truyen/ach-nan-thien-thu-ZXq3uFS4CE8G4a4M"
driver.get(web)
WebDriverWait(driver, 30).until(
    lambda d: d.execute_script('return document.readyState') == 'complete'
)


pagination = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "pagination"))
)

# Lấy tất cả các thẻ <li> bên trong thẻ <ul> đó
li_elements = pagination.find_elements(By.TAG_NAME, "li")
#-----------------
# Tìm thẻ <ul> đầu tiên có class "pagination"
# Tìm thẻ <ul> đầu tiên có class "pagination"
pagination_locator = (By.CLASS_NAME, "pagination")
# Hàm thu thập tất cả href từ các thẻ //li[@class="chapter-name"] và lưu vào file JSON
# Hàm thu thập tất cả href từ các thẻ //li[@class="chapter-name"] và lưu vào file JSON
def collect_chapters_and_save():
    # Danh sách lưu trữ href từ trang hiện tại
    chapter_links = []

    # Tìm tất cả các thẻ <li> với class "chapter-name" (duyệt từ trên xuống)
    chapter_elements = driver.find_elements(By.XPATH, '//li[@class="chapter-name"]')
    for chapter in chapter_elements:
        try:
            # Lấy href từ thẻ <a> bên trong
            a_tag = chapter.find_element(By.TAG_NAME, "a")
            href = a_tag.get_attribute("href")
            if href:  # Kiểm tra href có giá trị
                chapter_links.append(href)  # Thứ tự lấy từ trên xuống
        except Exception as e:
            print(f"Lỗi khi lấy href từ chapter: {e}")

    # Đường dẫn file JSON để lưu
    output_file = os.path.join(current_dir, "url_requests.json")

    # Nếu file đã tồn tại, mở và nối thêm dữ liệu
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
                existing_links = existing_data.get("chapter_links", [])
            except json.JSONDecodeError:
                existing_links = []
    else:
        existing_links = []

    # Kết hợp danh sách cũ với danh sách mới (tránh trùng lặp)
    all_links = existing_links + [link for link in chapter_links if link not in existing_links]

    # Ghi dữ liệu ra file JSON (vẫn giữ thứ tự ban đầu từ trên xuống)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"chapter_links": all_links}, f, ensure_ascii=False, indent=4)

    print(f"Đã lưu {len(chapter_links)} link chapter từ trang hiện tại vào file {output_file}.")

while True:
    try:
        # Lấy lại danh sách các thẻ <li> mỗi khi cần
        pagination = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(pagination_locator)
        )
        li_elements = pagination.find_elements(By.TAG_NAME, "li")

        # Lặp qua danh sách thẻ <li>, bắt đầu từ thẻ thứ 2 (index = 1)
        for index in range(1, len(li_elements)):  # Bắt đầu từ index = 1
            # Lấy lại danh sách thẻ <li> vì DOM có thể đã thay đổi
            pagination = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(pagination_locator)
            )
            #gọi hàm
            collect_chapters_and_save()

            li_elements = pagination.find_elements(By.TAG_NAME, "li")
            li_to_click = li_elements[index]
            # Click vào thẻ <li>
            li_to_click.click()
            time.sleep(1)
            # Chờ đợi trang tải xong
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )

            # Log trạng thái
            print(f"Đã click vào thẻ <li> thứ {index + 1} và trang đã tải xong.")

            # Kiểm tra nếu đây là phần tử cuối cùng
            if index == len(li_elements) - 1:
                print("Đã tới phần tử pagination cuối cùng.")
                break
        else:
            # Nếu không break trong for, tiếp tục vòng while
            continue
        break  # Thoát khỏi vòng lặp while nếu break trong for
    except Exception as e:
        print(f"Lỗi khi click vào thẻ <li>: {e}")
        break


# Thay thế time.sleep(10) bằng hàm đợi trang web tải xong
WebDriverWait(driver, 30).until(
    lambda d: d.execute_script('return document.readyState') == 'complete'
)

# Đóng trình duyệt
driver.quit()
