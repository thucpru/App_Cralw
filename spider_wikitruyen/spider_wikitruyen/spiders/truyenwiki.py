import scrapy
import re
import json
from unidecode import unidecode  # Để xử lý bỏ dấu tiếng Việt
import os

class TruyenwikiSpider(scrapy.Spider):
    name = "truyenwiki"
    allowed_domains = ["truyenwikidich.net"]
    # start_urls = ["https://truyenwikidich.net/truyen/ach-nan-thien-thu-ZXq3uFS4CE8G4a4M"]
    # Đọc file links.json để lấy URL đầu tiên
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Thư mục hiện tại của file Spider
    json_path = os.path.join(current_dir, "../links.json") 
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    start_urls = [data["urls"][0]]  # Chỉ lấy URL đầu tiên

    def create_slug(self, name):
        """
        Tạo slug từ tên (tác giả hoặc truyện).
        """
        # Bỏ dấu tiếng Việt và chuyển chữ thường
        slug = unidecode(name).lower()
        # Thay khoảng trắng và các ký tự không hợp lệ bằng dấu gạch ngang
        slug = re.sub(r'\s+', '-', slug)  # Thay khoảng trắng bằng dấu '-'
        slug = re.sub(r'[^a-z0-9\-]', '', slug)  # Loại bỏ ký tự không hợp lệ
        return slug.strip('-')

    def parse(self, response):
        # Lấy tên tác giả từ trang web
        author = response.xpath('//p[contains(text(), "Tác giả")]/a/text()').get()
        # Lấy tên truyện từ trang web
        story_name = response.xpath("//h2/text()").get()  # Giả sử tên truyện nằm trong thẻ h1
        # Lấy mô tả truyện từ trang web
        desc = response.xpath("//div[contains(@class, 'book-desc-detail')]/p/text()").getall()
        desc_text = " ".join(desc).strip()

        if author and story_name:
            # Tạo slug từ tên tác giả
            author_slug = self.create_slug(author)
            # Tạo slug từ tên truyện
            story_slug = self.create_slug(story_name)

            # Truyền dữ liệu vào item
            yield {
                "authors": author,
                "author_slug": author_slug,  # Slug của tác giả
                "story_slug": story_slug,  # Slug của truyện
                "story_name": story_name,  # Tên truyện
                "story_image": "test.jpg",  # Giả định link ảnh
                "story_desc": desc_text,  # Nội dung mô tả lấy được
                "status": 1,
                "is_full": 0,
                "is_hot": 0,
                "is_new": 1
            }
        self.logger.info(f"Yielded item: {author}, {story_name}")
