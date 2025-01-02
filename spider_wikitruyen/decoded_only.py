import json
import os
import glob

def decode_jsonl(input_file):
    """
    Giải mã file JSONL từ định dạng Unicode sang tiếng Việt.

    Args:
    - input_file: Tên file JSONL cần giải mã.
    """
    try:
        # Tìm số thứ tự cho file đầu ra
        existing_files = glob.glob("decoded_results_*.jsonl")
        new_file_number = len(existing_files) + 1
        output_file = f"decoded_results_{new_file_number}.jsonl"

        # Mở file đầu vào và đầu ra
        with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
            for line in infile:
                data = json.loads(line)  # Đọc từng dòng JSON
                json.dump(data, outfile, ensure_ascii=False, indent=4)  # Lưu với ensure_ascii=False
                outfile.write("\n")  # Xuống dòng cho mỗi object
        print(f"File đã được giải mã và lưu vào: {output_file}")
    except Exception as e:
        print(f"Lỗi khi giải mã file: {e}")

def list_files_with_extension(extension):
    """
    Liệt kê tất cả các file trong thư mục hiện tại với phần mở rộng nhất định.

    Args:
    - extension: Phần mở rộng file (ví dụ: '.jsonl').

    Returns:
    - Danh sách các file với phần mở rộng đã chỉ định.
    """
    return [f for f in os.listdir() if f.endswith(extension)]

if __name__ == "__main__":
    # Liệt kê tất cả các file JSONL trong thư mục hiện tại
    jsonl_files = list_files_with_extension(".jsonl")

    if not jsonl_files:
        print("Không có file JSONL nào trong thư mục hiện tại.")
    else:
        # Hiển thị danh sách file JSONL
        print("Danh sách file JSONL có sẵn:")
        for idx, filename in enumerate(jsonl_files, start=1):
            print(f"{idx}. {filename}")

        # Yêu cầu người dùng chọn file
        try:
            choice = int(input("Nhập số thứ tự file cần decode: ")) - 1
            if 0 <= choice < len(jsonl_files):
                selected_file = jsonl_files[choice]
                print(f"Đang giải mã file: {selected_file}")
                decode_jsonl(selected_file)
            else:
                print("Lựa chọn không hợp lệ.")
        except ValueError:
            print("Vui lòng nhập số thứ tự hợp lệ.")
