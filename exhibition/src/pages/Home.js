import React from 'react';
import { Carousel } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './Home.css'; 


function Home() {
  return (
    <div className="container mt-4">
      <h1 className="text-center mb-4">🎨 歡迎來到展覽查詢平台</h1>

      {/* Carousel (滑動圖片) */}
      <Carousel>
        <Carousel.Item>
          <img
            className="carousel-img"
            src="/pictures/home/huashan.JPG"
            alt="第一張圖片"
          />
          <Carousel.Caption>
            <h3>探索最新的展覽</h3>
            <p>在這裡，你可以找到全台最熱門的展覽資訊！</p>
          </Carousel.Caption>
        </Carousel.Item>

        <Carousel.Item>
          <img
            className="carousel-img"
            src="/pictures/home/tainan_art2.jpg"
            alt="第二張圖片"
          />
          <Carousel.Caption>
            <h3>豐富的藝術文化</h3>
            <p>多種展覽分類，讓你盡情探索藝術的世界。</p>
          </Carousel.Caption>
        </Carousel.Item>

        <Carousel.Item>
          <img
            className="carousel-img"
            src="/pictures/home/taichung.jpg"
            alt="第三張圖片"
          />
          <Carousel.Caption>
            <h3>線上預約更方便</h3>
            <p>立即查看展覽詳情，快速預約，省時省力！</p>
          </Carousel.Caption>
        </Carousel.Item>
      </Carousel>

      {/* 其他內容 */}
      <div className="text-center mt-4">
        <p>在這裡，你可以瀏覽最新的展覽資訊，發現最精彩的藝術活動。</p>
      </div>
    </div>
  );
}

export default Home;
