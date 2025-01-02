import os
import requests
from datetime import datetime

# API Key của bạn
API_KEY = "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"

# ID của batch mà bạn muốn kiểm tra
BATCH_ID = "batch_67757994ff34819093212d12ec3cc3c3"

# Headers cho API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
def check_and_download_batch(batch_id):
    try:
        # Kiểm tra trạng thái batch
        url = f"https://api.openai.com/v1/batches/{batch_id}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        # Lấy thông tin trạng thái
        batch_status = response.json()
        status = batch_status["status"]
        print(f"Trạng thái batch: {status}")

        # Nếu batch hoàn tất, tải file kết quả
        if status == "completed":
            output_file_id = batch_status["output_file_id"]
            print(f"Batch hoàn tất. Tải kết quả với file ID: {output_file_id}")

            # Tải file kết quả
            download_url = f"https://api.openai.com/v1/files/{output_file_id}/content"
            result_response = requests.get(download_url, headers=HEADERS)
            result_response.raise_for_status()

            # Tạo tên tệp mới
            base_filename = "translated_results"
            extension = ".jsonl"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{base_filename}_{timestamp}{extension}"

            # Lưu file kết quả
            with open(filename, "wb") as f:
                f.write(result_response.content)
            print(f"Kết quả đã được lưu vào: {filename}")
        elif status == "failed":
            print("Batch không thành công. Vui lòng kiểm tra file JSONL hoặc thông số batch.")
        else:
            print("Batch chưa hoàn tất. Trạng thái hiện tại:", status)
    except requests.exceptions.HTTPError as e:
        print(f"Lỗi HTTP: {e.response.status_code} - {e.response.text}")

# Gọi hàm kiểm tra và tải file
if __name__ == "__main__":
    check_and_download_batch(BATCH_ID)
