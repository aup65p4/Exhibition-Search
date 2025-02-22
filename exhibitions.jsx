import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Exhibitions() {
  const [exhibitions, setExhibitions] = useState([]);

  useEffect(() => {
    // 使用 axios 發送 GET 請求來獲取資料
    axios.get('http://localhost:5000/api/exhibitions')
      .then(response => {
        setExhibitions(response.data);  // 更新 state
      })
      .catch(error => {
        console.error("資料獲取失敗", error);
      });
  }, []);

  return (
    <div>
      <h1>展覽資訊</h1>
      <table>
        <thead>
          <tr>
            <th>展覽名稱</th>
            <th>展覽日期</th>
            <th>展覽時間</th>
            <th>連結</th>
            <th>類型</th>
          </tr>
        </thead>
        <tbody>
          {exhibitions.map((exhibition) => (
            <tr key={exhibition.id}>
              <td>{exhibition.name}</td>
              <td>{exhibition.date}</td>
              <td>{exhibition.time}</td>
              <td><a href={exhibition.link} target="_blank" rel="noopener noreferrer">更多資訊</a></td>
              <td>{exhibition.category}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Exhibitions;
