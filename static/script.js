document.getElementById("show-all").addEventListener("click", () => {
    fetchExhibitions("asc", "", "", "all", "所有展覽");
});

document.getElementById("show-current").addEventListener("click", () => {
    fetchExhibitions("asc", "", "", "current", "目前展覽");
});

document.getElementById("show-future").addEventListener("click", () => {
    fetchExhibitions("asc", "", "", "future", "未來展覽");
});

function fetchExhibitions(order, startDate, endDate, type, title) {
    fetch("/get_exhibitions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order, startDate, endDate, type })
    })
    .then(response => response.json())
    .then(data => {
        let exhibitions = data.exhibitions;
        let container = document.getElementById("exhibition-list");
        let titleElement = document.getElementById("exhibition-title");

        // 更新標題
        titleElement.innerText = title;

        // 清空展覽列表
        container.innerHTML = "";

        // 取得今天的日期
        const today = new Date();
        const todayDateString = today.toISOString().split('T')[0];  // YYYY-MM-DD 格式

        exhibitions.forEach(exhibition => {
            // 取得展覽的開始與結束日期
            const [startDate, endDate] = exhibition.date.split(' - '); 
            let exhibitionType = "";

            // 將開始與結束日期轉換為 Date 物件
            const startExhibitionDate = convertToDate(startDate);
            let endExhibitionDate = endDate ? convertToDate(endDate) : startExhibitionDate; // 若無結束日期，使用開始日期

            // 判斷展覽是否應該顯示為「目前展覽」或「未來展覽」
            if (startExhibitionDate <= today && endExhibitionDate >= today) {
                exhibitionType = "current"; // 當前展覽
            } else if (startExhibitionDate > today) {
                exhibitionType = "future"; // 未來展覽
            }

            // 根據 type 顯示
            if (type === "all" || exhibitionType === type) {
                let card = `
                    <div class="card">
                        <a href="${exhibition.link}" target="_blank">
                            <div class="card-img" style="background-image: url('${exhibition.image}');"></div>
                        </a>
                        <div class="card-content">
                            <h2><a href="${exhibition.link}" target="_blank">${exhibition.name}</a></h2>
                            <p><strong>日期：</strong>${exhibition.date}</p>
                            <p><strong>時間：</strong>${exhibition.time}</p>
                            <p><strong>類別：</strong>${exhibition.category}</p>
                            <a href="${exhibition.link}" class="btn">了解更多</a>
                        </div>
                    </div>
                `;
                container.innerHTML += card;
            }
        });
    })
    .catch(error => console.error("Error fetching exhibitions:", error));
}

// 日期轉換為 Date 物件，處理 YYYY.MM.DD 格式
function convertToDate(dateString) {
    const [year, month, day] = dateString.split('.').map(num => parseInt(num, 10));
    return new Date(year, month - 1, day);  // JavaScript 的月份從 0 開始
}
</script>
