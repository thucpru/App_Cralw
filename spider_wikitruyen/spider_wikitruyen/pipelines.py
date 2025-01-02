# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymysql
import logging

class SpiderWikitruyenPipeline:
    def open_spider(self, spider):
        try:
            # Kết nối tới cơ sở dữ liệu
            self.conn = pymysql.connect(
                host="localhost",
                user="admin",  # Thay bằng user của bạn
                password="admin",  # Thay bằng mật khẩu của bạn
                database="db_source_truyen",  # Tên cơ sở dữ liệu
                charset="utf8mb4"  # Đảm bảo hỗ trợ tiếng Việt
            )
            self.cursor = self.conn.cursor()
            logging.warning("Đã kết nối database")
        except pymysql.MySQLError as err:
            logging.error(f"Thất bại kết nối database: {err}")
            self.conn = None
            self.cursor = None

    def close_spider(self, spider):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logging.warning("Disconnected from database")

    def get_or_create_author_id(self, author_name, author_slug):
        """
        Kiểm tra xem tác giả đã tồn tại chưa. Nếu tồn tại, trả về id.
        Nếu chưa, thêm mới và trả về id vừa thêm.
        """
        if not author_name or not author_slug:
            logging.error("Author name or slug is missing.")
            return None

        # Kiểm tra xem tác giả đã tồn tại hay chưa
        check_query = "SELECT id FROM authors WHERE name = %s"
        self.cursor.execute(check_query, (author_name,))
        result = self.cursor.fetchone()

        if result:
            # Nếu đã tồn tại, trả về id
            logging.info(f"Author exists: {author_name}, ID: {result[0]}")
            return result[0]
        else:
            # Nếu chưa tồn tại, thêm mới
            insert_query = """
                INSERT INTO authors (slug, name, created_at, updated_at)
                VALUES (%s, %s, NOW(), NOW())
            """
            try:
                self.cursor.execute(insert_query, (author_slug, author_name))
                self.conn.commit()
                author_id = self.cursor.lastrowid  # Lấy id của bản ghi vừa thêm
                logging.info(f"Author created: {author_name}, ID: {author_id}")
                return author_id
            except pymysql.MySQLError as err:
                logging.error(f"Error inserting author: {err}")
                self.conn.rollback()
                return None

    def check_and_insert_or_update_story(self, story_data):
        """
        Kiểm tra xem story đã tồn tại chưa. Nếu tồn tại, cập nhật các cột khác.
        Nếu chưa tồn tại, chèn dữ liệu mới vào bảng stories.
        """
        # Kiểm tra xem story đã tồn tại chưa dựa trên story_slug hoặc story_name
        check_story_query = "SELECT id FROM stories WHERE slug = %s OR name = %s"
        self.cursor.execute(check_story_query, (story_data['slug'], story_data['name']))
        result = self.cursor.fetchone()

        if result:
            # Nếu story đã tồn tại, cập nhật các cột khác
            story_id = result[0]
            update_story_query = """
                UPDATE stories
                SET image = %s, `desc` = %s, author_id = %s, status = %s, is_full = %s,
                    is_hot = %s, is_new = %s, updated_at = NOW()
                WHERE id = %s
            """
            try:
                self.cursor.execute(update_story_query, (
                    story_data['image'],
                    story_data['desc'],
                    story_data['author_id'],
                    story_data['status'],
                    story_data['is_full'],
                    story_data['is_hot'],
                    story_data['is_new'],
                    story_id
                ))
                self.conn.commit()
                logging.info(f"Updated story: {story_data['name']} with ID: {story_id}")
            except pymysql.MySQLError as err:
                logging.error(f"Error updating story '{story_data['name']}': {err}")
                self.conn.rollback()
        else:
            # Nếu story chưa tồn tại, chèn dữ liệu mới
            insert_story_query = """
                INSERT INTO stories (slug, image, name, `desc`, author_id, status, is_full, is_hot, is_new, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            try:
                self.cursor.execute(insert_story_query, (
                    story_data['slug'],
                    story_data['image'],
                    story_data['name'],
                    story_data['desc'],
                    story_data['author_id'],
                    story_data['status'],
                    story_data['is_full'],
                    story_data['is_hot'],
                    story_data['is_new']
                ))
                self.conn.commit()
                logging.info(f"Inserted new story: {story_data['name']}")
            except pymysql.MySQLError as err:
                logging.error(f"Error inserting story '{story_data['name']}': {err}")
                self.conn.rollback()

    def process_item(self, item, spider):
        """
        Xử lý từng item được truyền từ Spider.
        """
        logging.info(f"Processing item: {item}")  # Log chi tiết item nhận được

        # Lấy thông tin từ item
        author_name = item.get("authors", "").strip()
        author_slug = item.get("author_slug", "").strip()
        story_slug = item.get("story_slug", "").strip()
        story_name = item.get("story_name", "").strip()

        # Kiểm tra các trường quan trọng
        if not author_name or not author_slug:
            logging.error("Missing author name or slug. Skipping item.")
            return item
        if not story_name or not story_slug:
            logging.error("Missing story name or slug. Skipping item.")
            return item

        # Kiểm tra hoặc tạo tác giả
        author_id = self.get_or_create_author_id(author_name, author_slug)

        # Chuẩn bị dữ liệu để chèn hoặc cập nhật bảng stories
        story_data = {
            "slug": story_slug,
            "image": item.get("story_image", "").strip(),
            "name": story_name,
            "desc": item.get("story_desc", "").strip(),
            "author_id": author_id,
            "status": item.get("status", 1),  # Mặc định là active
            "is_full": item.get("is_full", 0),  # Mặc định là chưa full
            "is_hot": item.get("is_hot", 0),  # Mặc định không hot
            "is_new": item.get("is_new", 1)  # Mặc định là mới
        }

        # Kiểm tra và chèn hoặc cập nhật dữ liệu story
        self.check_and_insert_or_update_story(story_data)

        return item
