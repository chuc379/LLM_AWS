import boto3
import time
from boto3.dynamodb.conditions import Key

# 1. Cấu hình kết nối AWS
dynamodb = boto3.resource(
    'dynamodb',
    region_name='ap-southeast-1', # Chọn region của bạn
    aws_access_key_id='AKIAWNREQUNE6TK6Y5M7',
    aws_secret_access_key='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'
)

table = dynamodb.Table('UserChatHistory')

def save_chat_turn(user_id, user_prompt, ai_response):
    """Lưu một lượt chat vào DynamoDB"""
    timestamp = int(time.time())
    ttl = timestamp + (24 * 3600)  # Tự xóa sau 24 giờ
    
    table.put_item(Item={
        'user_id': user_id,
        'timestamp': timestamp,
        'chat_data': {
            'user': user_prompt,
            'bot': ai_response
        },
        'ttl': ttl
    })

def get_recent_history(user_id, limit=5):
    """Lấy N tin nhắn gần nhất của user_id từ JWT"""
    response = table.query(
        KeyConditionExpression=Key('user_id').eq(user_id),
        ScanIndexForward=False, # Lấy tin nhắn mới nhất trước
        Limit=limit
    )
    return response.get('Items', [])

# --- VÍ DỤ SỬ DỤNG ---
# Giả sử bạn đã giải mã JWT và có user_id = "user_123"
user_id_from_jwt = "user_123"

# 1. Lấy lịch sử cũ để đưa vào Gemini Prompt
history = get_recent_history(user_id_from_jwt)
print(f"Lịch sử gần đây: {history}")

# 2. Sau khi Gemini trả lời, lưu lượt chat mới
