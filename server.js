const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');

// 初始化 Express 應用
const app = express();
const port = 5000;

// 允許跨域請求
app.use(cors());

// 設定 MySQL 連接
const db = mysql.createConnection({
  host: 'localhost',    // MySQL 主機
  user: 'root',         // 使用者名稱
  password: 'P@ssw0rd',  // 密碼
  database: 'exhibition_db'   // 資料庫名稱
});

// 測試資料庫連接
db.connect((err) => {
  if (err) {
    console.error('資料庫連線失敗:', err.stack);
    return;
  }
  console.log('成功連線到資料庫');
});

// 建立 API 路由：取得所有展覽資料
app.get('/api/exhibitions', (req, res) => {
  db.query('SELECT * FROM exhibitions', (err, results) => {
    if (err) {
      res.status(500).send('資料庫查詢錯誤');
      return;
    }
    res.json(results); // 返回查詢結果
  });
});

// 啟動伺服器
app.listen(port, () => {
  console.log(`伺服器運行在 http://localhost:${port}`);
});
