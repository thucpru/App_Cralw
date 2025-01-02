import json
import time
import requests
import os

# OpenAI API Key
API_KEY = "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"

# Đường dẫn file
INPUT_JSON = "output_chapters.json"  # File đầu vào chứa các chương truyện
OUTPUT_JSONL = "requests.jsonl"      # File JSONL cần tạo
OUTPUT_FILE = "translated_results.jsonl"  # File kết quả
# Kiểm tra file đầu vào
if not os.path.exists(INPUT_JSON):
    raise FileNotFoundError(f"File đầu vào không tồn tại: {INPUT_JSON}")

# Headers cho API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def convert_json_to_jsonl():
    """
    Chuyển đổi file JSON sang định dạng JSONL với custom_id là số chương.
    """
    with open(INPUT_JSON, "r", encoding="utf-8") as infile, open(OUTPUT_JSONL, "w", encoding="utf-8") as outfile:
        chapters = json.load(infile)
        for chapter in chapters:
            # Lấy số chương từ trường "chapter"
            chapter_number = chapter.get("chapter", "unknown")
            
            # Nội dung prompt cho từng chương
            content = f"Dịch lại truyện convert sau giống như tiểu thuyết gia chuyên nghiệp.\n\nNội dung: {chapter['content']}"
            
            # Dòng JSONL cho chương
            request_data = {
                "custom_id": str(chapter_number),  # Dùng số chương làm custom_id
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o-mini",  # Sử dụng model gpt-4o-mini
                    "messages": [
                        {"role": "user", "content": content}
                    ],
                    "temperature": 0.7,  # Độ sáng tạo của câu trả lời
                    "top_p": 0.9 # Tính xác suất của các từ đầu ra
                }
            }
            # Ghi từng dòng vào file JSONL
            outfile.write(json.dumps(request_data, ensure_ascii=False) + "\n")
    print(f"File JSONL đã được tạo: {OUTPUT_JSONL}")


def validate_jsonl(file_path):
    """
    Kiểm tra định dạng file JSONL.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Lỗi JSON ở dòng {i}: {line.strip()}")
                raise e
    print(f"File JSONL hợp lệ: {file_path}")

def upload_file():
    """
    Tải file JSONL lên OpenAI và trả về file_id.
    """
    with open(OUTPUT_JSONL, "rb") as f:
        response = requests.post(
            "https://api.openai.com/v1/files",
            headers={
                "Authorization": f"Bearer {API_KEY}"
            },
            files={"file": (OUTPUT_JSONL, f)},
            data={"purpose": "batch"}
        )
        response.raise_for_status()
        file_id = response.json()["id"]
        print(f"File đã được tải lên với ID: {file_id}")
        return file_id

def create_batch(file_id):
    """
    Tạo batch từ file đã tải lên.
    """
    data = {
        "input_file_id": file_id,
        "endpoint": "/v1/chat/completions",  # Endpoint cho ChatGPT
        "completion_window": "24h"
    }
    response = requests.post("https://api.openai.com/v1/batches", headers=HEADERS, json=data)
    response.raise_for_status()
    batch_id = response.json()["id"]
    print(f"Batch đã được tạo với ID: {batch_id}")
    return batch_id

def check_batch_status(batch_id):
    """
    Theo dõi trạng thái của batch cho đến khi hoàn thành.
    """
    while True:
        response = requests.get(f"https://api.openai.com/v1/batches/{batch_id}", headers=HEADERS)
        response.raise_for_status()
        batch_status = response.json()
        status = batch_status["status"]
        print(f"Trạng thái batch: {status}")
        if status == "completed":
            return batch_status["output_file_id"]
        elif status in ["failed", "cancelled"]:
            raise Exception(f"Batch không thành công với trạng thái: {status}")
        time.sleep(10)

def download_output_file(output_file_id):
    """
    Tải file kết quả đầu ra.
    """
    response = requests.get(f"https://api.openai.com/v1/files/{output_file_id}/content", headers=HEADERS)
    response.raise_for_status()
    with open(OUTPUT_FILE, "wb") as f:
        f.write(response.content)
    print(f"Kết quả đã được lưu vào: {OUTPUT_FILE}")

def main():
    # Bước 1: Chuyển đổi JSON sang JSONL
    convert_json_to_jsonl()

    # Bước 2: Kiểm tra file JSONL
    validate_jsonl(OUTPUT_JSONL)

    # Bước 3: Upload file JSONL lên OpenAI
    file_id = upload_file()

    # Bước 4: Tạo batch
    batch_id = create_batch(file_id)

    # Bước 5: Kiểm tra trạng thái batch
    output_file_id = check_batch_status(batch_id)

    # Bước 6: Tải kết quả
    download_output_file(output_file_id)

if __name__ == "__main__":
    main()
