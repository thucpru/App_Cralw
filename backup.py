import scrapy
import re
import unidecode
import json
import os


class ChapterwikiSpider(scrapy.Spider):
    name = "chapterwiki"
    allowed_domains = ["www.truyenwikidich.net"]
    start_urls = [
        "https://www.truyenwikidich.net/truyen/ach-nan-thien-thu/chuong-1-hoa-khoi-thai-thuy-dien-ZXq3ucQsRAL2~WM2"
    ]
    output_file = "chapter_content.json"  # Tên file JSON sẽ được ghi

    def parse(self, response):
        # Lấy dữ liệu từ response
        name = response.xpath("//div[@id='bookContent']/p[2]/text()").get(default="").strip()
        splitted = name.split()
        chapter = ""
        if len(splitted) >= 2:
            chapter = re.sub(r"[^0-9]", "", splitted[1])
        slug = self.slugify(name)
        content = response.xpath("//div[@id='bookContentBody']").get()

        # Dữ liệu để ghi vào file JSON
        data = {
            "chapter": chapter,
            "name": name,
            "slug": slug,
            "content": content
        }

        # Ghi dữ liệu vào file JSON
        self.save_to_file(data)

    def slugify(self, text):
        text = unidecode.unidecode(text)
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = text.strip('-')
        return text

    def save_to_file(self, data):
        # Kiểm tra nếu file tồn tại, ghi thêm; nếu không, tạo file mới
        file_exists = os.path.isfile(self.output_file)
        with open(self.output_file, "a" if file_exists else "w", encoding="utf-8") as f:
            if file_exists:
                f.write(",\n")  # Dòng mới nếu đã có dữ liệu trong file
            else:
                f.write("[\n")  # Mở danh sách JSON mới
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.write("\n]")  # Đóng danh sách JSON

    def closed(self, reason):
        # Khi spider đóng, loại bỏ dấu phẩy thừa ở cuối file JSON
        if os.path.isfile(self.output_file):
            with open(self.output_file, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.rstrip(",\n]") + "\n]"
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(content)
#==========================================================================================================

import scrapy
import re
import unidecode
import json
import os
import spider_wikitruyen.xhr_chapter    # Import module xhr_chapter.py

class ChapterwikiSpider(scrapy.Spider):
    name = "chapterwiki"
    allowed_domains = ["www.truyenwikidich.net", "truyenwikidich.net"]
    output_file = "chapter_content.json"  # Tên file JSON sẽ được ghi
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    xhr_file = os.path.join(base_dir, "xhr_requests.json")  # Đường dẫn tới file JSON
    
    def start_requests(self):
        """Khởi động spider từ file JSON chứa danh sách URL."""
        with open(self.xhr_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            # Lấy danh sách URL từ file JSON
            urls = [entry["url"] for entry in data]
            
        # Gửi request tới từng URL
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_chapters)

    def parse_chapters(self, response):
        """Phân tích và lấy danh sách href từ các thẻ li[class=chapter-name]."""
        # Lấy tất cả các URL chương từ các thẻ li[class=chapter-name]
        chapters = response.xpath('//li[@class="chapter-name"]/a/@href').getall()

        for chapter in chapters:
            # Tạo URL đầy đủ nếu chapter là liên kết tương đối
            base_url = f"https://{self.allowed_domains[0]}"  # Sử dụng domain từ allowed_domains
            chapter_url = chapter if chapter.startswith("http") else base_url + chapter  # Kiểm tra nếu là liên kết tuyệt đối
            self.log(f"Found chapter URL: {chapter_url}")
            yield scrapy.Request(url=chapter_url, callback=self.parse_content)

    def parse_content(self, response):
        # Lấy dữ liệu từ response
        name = response.xpath("//div[@id='bookContent']/p[2]/text()").get(default="").strip()
        splitted = name.split()
        chapter = ""
        if len(splitted) >= 2:
            chapter = re.sub(r"[^0-9]", "", splitted[1])
        slug = self.slugify(name)
        content = response.xpath("//div[@id='bookContentBody']").get()

        # Dữ liệu để ghi vào file JSON
        data = {
            "chapter": chapter,
            "name": name,
            "slug": slug,
            "content": content
        }

        # Ghi dữ liệu vào file JSON
        self.save_to_file(data)

    def slugify(self, text):
        text = unidecode.unidecode(text)
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = text.strip('-')
        return text

    def save_to_file(self, data):
        # Kiểm tra nếu file tồn tại, ghi thêm; nếu không, tạo file mới
        file_exists = os.path.isfile(self.output_file)
        with open(self.output_file, "a" if file_exists else "w", encoding="utf-8") as f:
            if file_exists:
                f.write(",\n")  # Dòng mới nếu đã có dữ liệu trong file
            else:
                f.write("[\n")  # Mở danh sách JSON mới
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.write("\n]")  # Đóng danh sách JSON

    def closed(self, reason):
        # Khi spider đóng, loại bỏ dấu phẩy thừa ở cuối file JSON
        if os.path.isfile(self.output_file):
            with open(self.output_file, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.rstrip(",\n]") + "\n]"
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(content)
#==========================================================================================================


api_key = "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"

# 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

# File đã được tải lên với ID: file-RQwzDNbdveEKPJQoYta52a
# Batch đã được tạo với ID: batch_677564a586f08190a3391ccca3e98760
file-1wNLTATH8HX6EpyhrvvB2f
batch_67756a4338bc8190b538f85d15010d18
batch_67757994ff34819093212d12ec3cc3c3