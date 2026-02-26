import requests
import json

# URL Lambda của bạn
base_url = "https://u5i3ebl4fjwvayvblmbfkwousu0hmubn.lambda-url.ap-southeast-1.on.aws"
openapi_url = f"{base_url}/openapi.json"

def get_all_endpoints():
    try:
        print(f"📡 Đang kết nối tới: {openapi_url}...")
        response = requests.get(openapi_url)
        
        if response.status_code == 200:
            data = response.json()
            paths = data.get("paths", {})
            
            print(f"\n✅ Tìm thấy {len(paths)} nhóm Endpoint hợp lệ:\n")
            print(f"{'METHOD':<10} | {'ENDPOINT PATH':<50}")
            print("-" * 65)
            
            for path, methods in paths.items():
                for method in methods.keys():
                    print(f"{method.upper():<10} | {path:<50}")
            
            print("\n💡 Lưu ý: Nếu FE gọi thiếu hoặc thừa dấu '/' so với danh sách trên, bạn sẽ bị 404.")
            
        else:
            print(f"❌ Không thể truy cập bản đồ API. Mã lỗi: {response.status_code}")
            print("Có thể Lambda đang bị Timeout hoặc lỗi khởi tạo (Cold Start).")
            
    except Exception as e:
        print(f"💥 Lỗi kết nối: {e}")

if __name__ == "__main__":
    get_all_endpoints()