import requests
import time
import os

def check_proxy(proxy):
    try:
        # Tách IP, port, username, password
        ip, port, user, password = proxy.split(":")
        proxies = {
            "http": f"http://{user}:{password}@{ip}:{port}",
            "https": f"http://{user}:{password}@{ip}:{port}"
        }
        # Gửi request đến một trang hiển thị IP (httpbin)
        response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
        
        # Nếu thành công, in ra proxy và IP được trả về
        if response.status_code == 200:
            print(f"Proxy {proxy} hoạt động! IP: {response.json()['origin']}")
        else:
            print(f"Proxy {proxy} không hoạt động (HTTP {response.status_code})")
    except Exception as e:
        print(f"Proxy {proxy} không hoạt động. Lỗi: {e}")

# Xác định đường dẫn file proxy
base_dir = os.path.dirname(os.path.abspath(__file__))  # Lấy thư mục chứa script
proxy_file_path = os.path.join(base_dir, "Webshare 10 proxies.txt")  # Đường dẫn đầy đủ đến file proxy

# Đọc danh sách proxy từ file
with open(proxy_file_path, "r") as file:
    proxies = [line.strip() for line in file]

# Kiểm tra từng proxy (chờ 10s giữa mỗi lần kiểm tra)
for proxy in proxies:
    check_proxy(proxy)
    # time.sleep(10)  # Chờ 10 giây trước khi kiểm tra proxy tiếp theo
