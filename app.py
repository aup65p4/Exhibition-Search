from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_exhibitions(order="asc", start_date="", end_date="", type_filter="all"):
    conn = sqlite3.connect("exhibitions.db")  # 資料庫檔案名稱為 exhibitions.db
    cursor = conn.cursor()

    # 修改查詢的資料表為 huashan1914
    query = "SELECT name, date, time, link, image, category FROM huashan1914"  
    params = []

    # 解析日期
    today = datetime.today().strftime("%Y.%m.%d")

    # 篩選條件
    if type_filter == "future":
        query += " WHERE date >= ?"
        params.append(today)
    elif type_filter == "current":
        query += " WHERE date < ?"
        params.append(today)

    # 排序
    if order == "desc":
        query += " ORDER BY date DESC"
    else:
        query += " ORDER BY date ASC"

    cursor.execute(query, params)
    exhibitions = cursor.fetchall()
    conn.close()

    return [{"name": e[0], "date": e[1], "time": e[2], "link": e[3], "image": e[4], "category": e[5]} for e in exhibitions]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_exhibitions", methods=["POST"])
def fetch_exhibitions():
    data = request.json
    order = data.get("order", "asc")
    start_date = data.get("startDate", "")
    end_date = data.get("endDate", "")
    type_filter = data.get("type", "all")

    exhibitions = get_exhibitions(order, start_date, end_date, type_filter)
    return jsonify({"exhibitions": exhibitions})

if __name__ == "__main__":
    app.run(debug=True)
