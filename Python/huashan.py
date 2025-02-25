import mysql.connector
import requests
from bs4 import BeautifulSoup
import re

# 網頁 URL
base_url = "https://www.huashan1914.com"
url = base_url + "/w/huashan1914/exhibition"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
}

# 連接 MySQL 資料庫
conn = mysql.connector.connect(
    host="localhost",        # MySQL 主機
    user="root",             # MySQL 使用者名稱
    password="P@ssw0rd",     # MySQL 密碼
    database="exhibition_db" # MySQL 資料庫名稱
)
cursor = conn.cursor()

# 確保表格包含 location 欄位
cursor.execute('''
    CREATE TABLE IF NOT EXISTS exhibitions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE,
        date VARCHAR(255),
        time VARCHAR(255),
        link TEXT,
        image TEXT,
        category VARCHAR(255),
        location VARCHAR(255)
    )
''')

def normalize_date(date_text):
    """統一日期格式為 YYYY.MM.DD - YYYY.MM.DD，補全省略的年份"""
    date_parts = date_text.split(" - ")
    
    if len(date_parts) == 2:
        start_date = date_parts[0].strip()
        end_date = date_parts[1].strip()

        # 使用正則表達式解析日期
        start_match = re.match(r"(\d{4})\.(\d{2})\.(\d{2})", start_date)
        end_match = re.match(r"(\d{2})\.(\d{2})", end_date)

        if start_match and end_match:
            # 提取開始日期的年份
            start_year = start_match.group(1)
            end_date = f"{start_year}.{end_date}"  # 統一補上年份

        return f"{start_date} - {end_date}"
    
    return date_text  # 若解析失敗則維持原始格式

def scrape_page(url):
    """爬取單頁並存入資料庫"""
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 取得所有展覽區塊 <li class="item-static">
    exhibitions = soup.find_all("li", class_="item-static")
    
    for exhibition in exhibitions:
        # 提取展覽名稱
        name_tag = exhibition.find("div", class_="card-text-name")
        name = name_tag.text.strip() if name_tag else "無標題"
    
        # 提取展覽日期，並格式化
        date_tag = exhibition.find("div", class_="event-date")
        raw_date = " - ".join([span.text.strip() for span in date_tag.find_all("span")]) if date_tag else "未提供日期"
        date = normalize_date(raw_date)  # 統一日期格式
    
        # 提取展覽時間
        time_tag = exhibition.find("div", class_="event-time")
        time = " - ".join([span.text.strip() for span in time_tag.find_all("span")]) if time_tag else "未提供時間"
    
        # 提取超連結
        link_tag = exhibition.find("a")
        link = base_url + link_tag.get("href") if link_tag else "無連結"
    
        # 提取圖片
        image_tag = exhibition.find("div", class_="card-img")
        style_attr = image_tag.get("style", "") if image_tag else ""
        image_url = style_attr.split("url('")[-1].split("')")[0] if "url('" in style_attr else "無圖片"
    
        # 提取展覽類型
        category_tag = exhibition.find("div", class_="event-list-type")
        category_span = category_tag.find("span") if category_tag else None
        category = category_span.text.strip() if category_span else "未提供類型"

        # 提取展覽地點
        location = "華山"
    
        # 檢查資料是否已存在
        cursor.execute("SELECT date, time, link, image, category, location FROM exhibitions WHERE name = %s", (name,))
        existing_entry = cursor.fetchone()
    
        if existing_entry:
            # 解包現有資料
            existing_date, existing_time, existing_link, existing_image, existing_category, existing_location = existing_entry
    
            # 如果資料不同，則更新
            if (date != existing_date or time != existing_time or link != existing_link 
                or image_url != existing_image or category != existing_category or location != existing_location):
    
                cursor.execute(""" 
                    UPDATE exhibitions 
                    SET date=%s, time=%s, link=%s, image=%s, category=%s, location=%s
                    WHERE name=%s
                """, (date, time, link, image_url, category, location, name))
                print(f"已更新展覽: {name} - {category} - {date} - {time} - {location} - {link} - {image_url}")
            else:
                print(f"無變更: {name}")
        else:
            # 新增資料
            cursor.execute("""
                INSERT INTO exhibitions (name, date, time, link, image, category, location) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, date, time, link, image_url, category, location))
            print(f"已新增展覽: {name} - {category} - {date} - {time} - {location} - {link} - {image_url}")
    
    # 提交變更
    conn.commit()

def scrape_all_pages(start_url):
    """爬取所有頁面，直到找不到「下一頁」"""
    current_url = start_url
    while current_url:
        print(f"正在爬取：{current_url}")
        scrape_page(current_url)
        
        # 查找下一頁的連結
        soup = BeautifulSoup(requests.get(current_url, headers=headers).text, "html.parser")
        next_page_tag = soup.find("a", rel="next")  # 根據提供的原始碼，尋找 rel="next" 的 <a> 標籤
        if next_page_tag and next_page_tag.get("href"):
            current_url = base_url + next_page_tag.get("href")
        else:
            current_url = None  # 如果沒有「下一頁」，則停止爬取

# 開始爬取
scrape_all_pages(url)

# 關閉資料庫連線
conn.close()

print("資料更新完成！")
