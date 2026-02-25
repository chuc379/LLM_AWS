import google.generativeai as genai

# Điền API Key của bạn vào đây
GENAI_API_KEY = "AIzaSyDVJBtZe27XWD3aVBha-t25XinVjEQmnQI"
genai.configure(api_key=GENAI_API_KEY)

print("--- Đang kiểm tra danh sách model hỗ trợ Embedding ---")

try:
    available_models = genai.list_models()
    found = False
    
    for m in available_models:
        # Kiểm tra xem model có hỗ trợ phương thức tạo embedding không
        if 'embedContent' in m.supported_generation_methods:
            print(f"Model Name: {m.name}")
            print(f"  > Description: {m.description}")
            print(f"  > Input Token Limit: {m.input_token_limit}")
            print(f"  > Supported Methods: {m.supported_generation_methods}")
            print("-" * 30)
            found = True
            
    if not found:
        print("Không tìm thấy model nào hỗ trợ embedContent với API Key này.")
        
except Exception as e:
    print(f"Lỗi khi kết nối tới Gemini API: {e}")