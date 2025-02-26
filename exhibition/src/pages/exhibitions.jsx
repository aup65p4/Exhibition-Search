import React, { useEffect, useState } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import './exhibitions.css'; // 確保你的樣式檔案被引用

function Exhibitions() {
  const [exhibitions, setExhibitions] = useState([]);
  const [showCards, setShowCards] = useState(false); // 控制卡片顯示的狀態

  useEffect(() => {
    axios.get('http://localhost:5000/api/exhibitions')  // 爬蟲 API
      .then(response => {
        setExhibitions(response.data);
      })
      .catch(error => {
        console.error("資料獲取失敗", error);
      });
  }, []);

  return (
    <div className="container mt-4">
      <h1 className="text-center mb-4">🎨 展覽資訊</h1>

      {/* 按鈕用來切換展覽資訊的顯示狀態 */}
      <div className="text-center mb-4">
        <button 
          className="btn btn-primary" 
          onClick={() => setShowCards(!showCards)}
        >
          {showCards ? "隱藏展覽資訊" : "顯示展覽資訊"}
        </button>
      </div>

      {/* 只有當 showCards 為 true 時才顯示展覽資訊 */}
      {showCards && (
        <div className="row">
          {exhibitions.map((exhibition, index) => (
            <div className="col-md-6 mb-4" key={index}> {/* 每行顯示兩個卡片 */}
              <div className="card shadow-sm h-100">
                <div className="row g-0">
                  {/* 左側：圖片區域，占 6/12 */}
                  {exhibition.image !== "無圖片" && (
                    <div className="col-md-6">
                      <img 
                        src={exhibition.image} 
                        alt={exhibition.name} 
                        className="img-fluid rounded-start"
                        style={{ height: "100%", objectFit: "cover" }}
                      />
                    </div>
                  )}
                  
                  {/* 右側：資訊區域，占 6/12 */}
                  <div className="col-md-6 d-flex flex-column justify-content-between">
                    <div className="card-body">
                      <h5 className="card-title">{exhibition.name}</h5>
                      <p className="text-muted">{exhibition.category}</p>
                      <p className="card-text">
                        🏛 <strong>地點：</strong> {exhibition.location} <br />
                        📅 <strong>日期：</strong> {exhibition.date} <br />
                        ⏰ <strong>時間：</strong> {exhibition.time}
                      </p>
                      <a href={exhibition.link} className="btn btn-primary" target="_blank" rel="noopener noreferrer">
                        查看詳情
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Exhibitions;
