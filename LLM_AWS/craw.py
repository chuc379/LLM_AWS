import requests
from bs4 import BeautifulSoup
import boto3
import json
import time
import re

# --- CẤU HÌNH AWS (ĐIỀN TẠI ĐÂY) ---
AWS_ACCESS_KEY = "AKIAWNREQUNE6TK6Y5M7"
AWS_SECRET_KEY = "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"
AWS_REGION = "ap-southeast-1"  # Ví dụ: Singapore là ap-southeast-1, US East là us-east-1

S3_BUCKET_NAME = "knowknowledge-base-chuong"

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

def crawl_full_wikipedia(url):
    """Lấy toàn bộ nội dung văn bản bao gồm cả Table, List, Paragraph"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Lấy Tiêu đề
            title = soup.find('h1', id='firstHeading').text
            
            # 2. Loại bỏ các thành phần rác (script, style, nav, footer)
            for script_or_style in soup(["script", "style", "aside"]):
                script_or_style.decompose()

            # 3. Lấy nội dung trong khu vực chính của bài viết
            main_content = soup.find(id="mw-content-text")
            
            # get_text() sẽ lấy toàn bộ text từ <p>, <table>, <li>...
            full_text = main_content.get_text(separator='\n') 
            
            # Làm sạch khoảng trắng dư thừa
            clean_text = re.sub(r'\n\s*\n', '\n', full_text).strip()
            
            return {
                "title": title,
                "url": url,
                "content": clean_text,
                "timestamp": time.time()
            }
    except Exception as e:
        print(f"Lỗi khi crawl {url}: {e}")
    return None

def main():
    # 1. Đọc danh sách link
    try:
        with open("links.txt", "r") as f:
            links = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy links.txt")
        return

    # 2. Duyệt qua từng link
    for link in links:
        print(f"--- Đang xử lý: {link} ---")
        data = crawl_full_wikipedia(link)
        
        if data:
            # Tạo tên file an toàn từ tiêu đề (Ví dụ: "Tom_Brady.json")
            safe_title = re.sub(r'[^\w\s-]', '', data['title']).strip().replace(' ', '_')
            s3_key = f"datalake/raw_data/{safe_title}.json"
            
            # 3. Đẩy lên S3 dưới dạng file riêng biệt
            try:
                s3_client.put_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=s3_key,
                    Body=json.dumps(data, ensure_ascii=False, indent=4),
                    ContentType='application/json'
                )
                print(f"Đã lưu thành công lên S3: {s3_key}")
            except Exception as e:
                print(f"Lỗi khi tải lên S3: {e}")
        
        # Nghỉ 1 chút để tránh bị Wiki chặn
        time.sleep(1.5)

if __name__ == "__main__":
    main()