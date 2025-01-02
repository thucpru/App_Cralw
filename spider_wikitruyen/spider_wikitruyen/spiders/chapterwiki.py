import scrapy
import re
import unidecode
import json
import os
import random

class ChapterwikiSpider(scrapy.Spider):
    name = "chapterwiki"
    allowed_domains = ["www.truyenwikidich.net", "truyenwikidich.net"]
    start_urls = []
    
    # Lưu file output
    output_file = "output_chapters.json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Đọc file JSON để lấy danh sách link
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "..", "url_requests.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.start_urls = data.get("chapter_links", [])
        except Exception as e:
            self.logger.error(f"Lỗi khi đọc file url_requests.json: {e}")
            # Nếu đọc file lỗi hoặc không có link => dừng spider
            self.crawler.engine.close_spider(self, "Không thể load URL, dừng spider.")
    
    def start_requests(self):
        """
        Tạo request cho từng URL kèm errback & random headers.
        """
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                errback=self.handle_request_error,
                headers=self.get_random_headers()
            )

    def parse(self, response):
        """
        Lấy nội dung chương: tên chương, số chapter, slug và nội dung text.
        Dừng spider ngay nếu bị 403.
        """
        if response.status == 403:
            self.logger.error(f"HTTP 403 Forbidden: {response.url}")
            self.crawler.engine.close_spider(self, "Bị chặn 403")
            return

        # Lấy tên chương
        name = response.xpath("//div[@id='bookContent']/p[2]/text()").get()
        name = name.strip() if name else "Chưa rõ tiêu đề"

        # Lấy số chương (nếu có)
        splitted = name.split()
        chapter = ""
        if len(splitted) >= 2:
            chapter = re.sub(r"[^0-9]", "", splitted[1])

        # Tạo slug
        slug = self.slugify(name)

        # Lấy nội dung chương
        content_list = response.xpath("//div[@id='bookContentBody']//text()").getall()
        content = "\n".join(line.strip() for line in content_list if line.strip())

        # Đóng gói data
        data = {
            "chapter": chapter,
            "name": name,
            "slug": slug,
            "content": content,
        }

        # Lưu vào file (thay vì yield item)
        self.save_to_file(data)

    def handle_request_error(self, failure):
        """
        Dừng spider nếu request bị lỗi (thường là DNS, timeout, ...).
        """
        self.logger.error(repr(failure))
        self.crawler.engine.close_spider(self, "Gặp lỗi, dừng spider.")

    def slugify(self, text):
        """
        Tạo slug cơ bản (chuyển sang ASCII, lower, thay khoảng trắng = '-').
        """
        text = unidecode.unidecode(text)
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        return text.strip('-')

    def get_random_headers(self):
        """
        Trả về headers với user-agent ngẫu nhiên.
        """
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
        ]
        return {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                      "image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
            "Cache-Control": "max-age=0",
            "Referer": "https://www.google.com/",
        }

    def save_to_file(self, data):
        """
        Ghi dữ liệu vào file JSON (một danh sách lớn).
        """
        file_exists = os.path.isfile(self.output_file)
        if not file_exists:
            # Tạo mới, khởi đầu mảng JSON
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump([data], f, ensure_ascii=False, indent=4)
        else:
            # Đọc nội dung cũ -> append -> ghi lại
            with open(self.output_file, "r", encoding="utf-8") as f:
                try:
                    old_data = json.load(f)
                except json.JSONDecodeError:
                    old_data = []
            old_data.append(data)
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(old_data, f, ensure_ascii=False, indent=4)
