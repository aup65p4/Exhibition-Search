import sqlite3
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# 網頁 URL
base_url = "https://www.huashan1914.com"
url = base_url + "/w/huashan1914/exhibition"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
}

# 連接 SQLite 資料庫
conn = sqlite3.connect("exhibitions.db")
cursor = conn.cursor()

# 確保表格包含類型欄位 (若無則新增)，表格名稱改為 huashan1914
cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS huashan1914 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        date TEXT,
        time TEXT,
        link TEXT,
        image TEXT,
        category TEXT
    )
''')

def normalize_date(date_text):
    """統一日期格式為 YYYY.MM.DD - YYYY.MM.DD，補全省略的年份，並檢查是否過期"""
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

        # 檢查日期是否過期
        try:
            end_date_obj = datetime.strptime(end_date, "%Y.%m.%d")
            today = datetime.today()

            # 當結束日期等於今天時也應該視為有效
            if end_date_obj < today:
                return None  # 日期已過期
        except ValueError:
            return date_text  # 無法解析日期則返回原始格式
    
        return f"{start_date} - {end_date}"
    
    # 若只提供開始日期，則結束日期設為開始日期
    elif len(date_parts) == 1:
        start_date = date_parts[0].strip()
        try:
            start_date_obj = datetime.strptime(start_date, "%Y.%m.%d")
            today = datetime.today()

            # 當開始日期等於今天時也應該視為有效
            if start_date_obj < today:
                return None  # 日期已過期
        except ValueError:
            return date_text  # 無法解析日期則返回原始格式
        
        return f"{start_date} - {start_date}"  # 開始日期與結束日期相同
    
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
        
        # 如果日期已過期，則跳過這個展覽
        if date is None:
            print(f"展覽 {name} 已過期，跳過")
            continue
    
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
    
        # 檢查資料是否已存在
        cursor.execute("SELECT date, time, link, image, category FROM huashan1914 WHERE name = ?", (name,))
        existing_entry = cursor.fetchone()
    
        if existing_entry:
            # 解包現有資料
            existing_date, existing_time, existing_link, existing_image, existing_category = existing_entry
    
            # 如果資料不同，則更新
            if (date != existing_date or time != existing_time or link != existing_link 
                or image_url != existing_image or category != existing_category):
    
                cursor.execute(""" 
                    UPDATE huashan1914 
                    SET date=?, time=?, link=?, image=?, category=? 
                    WHERE name=? 
                """, (date, time, link, image_url, category, name))
                print(f"已更新展覽: {name} - {category} - {date} - {time} - {link} - {image_url}")
            else:
                print(f"無變更: {name}")
        else:
            # 新增資料
            cursor.execute(""" 
                INSERT INTO huashan1914 (name, date, time, link, image, category) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, date, time, link, image_url, category))
            print(f"已新增展覽: {name} - {category} - {date} - {time} - {link} - {image_url}")

        # 刪除已過期的展覽
        cursor.execute("SELECT id, date FROM huashan1914 WHERE date != ?", (date,))
        expired_exhibitions = cursor.fetchall()
        for exhibition_id, exhibition_date in expired_exhibitions:
            if exhibition_date and datetime.strptime(exhibition_date.split(" - ")[1], "%Y.%m.%d") < datetime.today():
                cursor.execute("DELETE FROM huashan1914 WHERE id = ?", (exhibition_id,))
                print(f"已刪除過期展覽: {name} - {exhibition_date}")

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

# 提交資料庫變更
conn.commit()

# 關閉資料庫連線
conn.close()

print("資料更新完成！")
1212