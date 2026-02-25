import boto3
import time
import google.generativeai as genai
from boto3.dynamodb.conditions import Key

class GeminiShortMemoryManager:
    def __init__(self, gemini_key, aws_access, aws_secret, region="ap-southeast-1"):
        # 1. Cấu hình Gemini
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel('gemini-3-flash-preview') # Cập nhật model mới nhất
        
        # 2. Cấu hình AWS DynamoDB
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=region,
            aws_access_key_id=aws_access,
            aws_secret_access_key=aws_secret
        )
        self.table = self.dynamodb.Table('UserChatHistory')

    def _get_recent_context(self, user_id, limit=5):
        """Lấy ngữ cảnh từ DynamoDB"""
        try:
            response = self.table.query(
                KeyConditionExpression=Key('user_id').eq(user_id),
                ScanIndexForward=False, # Lấy mới nhất trước
                Limit=limit
            )
            items = response.get('Items', [])
            items.reverse() # Đảo lại thứ tự thời gian cũ -> mới
            return items
        except Exception as e:
            print(f"Lỗi truy vấn DynamoDB: {e}")
            return []

    def _save_memory(self, user_id, prompt, response):
        """Lưu lượt chat mới vào AWS"""
        timestamp = int(time.time())
        ttl = timestamp + (24 * 3600) # Tự xóa sau 24h
        try:
            self.table.put_item(Item={
                'user_id': user_id,
                'timestamp': timestamp,
                'user_msg': prompt,
                'ai_msg': response,
                'ttl': ttl
            })
        except Exception as e:
            print(f"Lỗi lưu DynamoDB: {e}")

    def ask_gemini_with_short_memory(self, user_id, user_question):
        # 1. Lấy context
        history = self._get_recent_context(user_id)
        
        # 2. Xây dựng Prompt
        context_string = ""
        if history:
            context_string = "Lịch sử trò chuyện gần đây:\n"
            for chat in history:
                context_string += f"Người dùng: {chat['user_msg']}\nAI: {chat['ai_msg']}\n"
        
        full_prompt = f"{context_string}\nCâu hỏi mới: {user_question}\nAI hãy trả lời dựa trên ngữ cảnh nếu có."

        # 3. Gọi Gemini
        try:
            chat_response = self.model.generate_content(full_prompt)
            ai_text = chat_response.text
            
            # 4. Lưu lại
            self._save_memory(user_id, user_question, ai_text)
            return ai_text
        except Exception as e:
            return f"Lỗi AI: {str(e)}"

# --- KHỐI LỆNH MAIN ĐỂ TEST ---
if __name__ == "__main__":
    # Thông tin cấu hình (Nên giữ kín nếu không phải dự án học tập)
    GEMINI_KEY = ""
    AWS_ID = ""
    AWS_SECRET = ""

    # 1. Khởi tạo manager
    manager = GeminiShortMemoryManager(GEMINI_KEY, AWS_ID, AWS_SECRET)

    # 2. Giả lập ID người dùng (Trong thực tế cái này lấy từ JWT)
    # Bạn có thể đổi ID này để test xem AI có quên/nhớ theo từng User không
    test_user_id = "user_hoc_tap_001" 

    print("=== CHƯƠNG TRÌNH CHAT VỚI GEMINI + AWS SHORT MEMORY ===")
    print(f"Đang chat với User ID: {test_user_id}")
    print("Gõ 'exit' hoặc 'quit' để dừng cuộc trò chuyện.\n")

    while True:
        # Bước 3: Cho phép bạn nhập câu hỏi tùy ý từ bàn phím
        user_input = input("Bạn: ")

        # Thoát nếu người dùng muốn
        if user_input.lower() in ['exit', 'quit']:
            print("Tạm biệt!")
            break
        
        if not user_input.strip():
            continue

        # Bước 4: Gọi hàm xử lý (Lấy history AWS -> Hỏi Gemini -> Lưu AWS)
        print("AI đang suy nghĩ...")
        response = manager.ask_gemini_with_short_memory(test_user_id, user_input)
        
        print(f"Gemini: {response}")
        print("-" * 30)