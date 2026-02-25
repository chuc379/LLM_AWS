"""
Infrastructure - Short Memory Repository Implementation (DynamoDB)
"""
import boto3
import time
from boto3.dynamodb.conditions import Key
from typing import List
from datetime import datetime

import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from LLM_AWS.domain.repositories import IShortMemoryRepository
from LLM_AWS.domain.entities import ChatMessage


class DynamoDBShortMemoryRepository(IShortMemoryRepository):
    def __init__(self, aws_access: str, aws_secret: str, region: str = "ap-southeast-1"):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=region,
            aws_access_key_id=aws_access,
            aws_secret_access_key=aws_secret
        )
        self.table = self.dynamodb.Table('UserChatHistory')
    
    def get_recent_messages(self, user_id: str, limit: int = 5) -> List[ChatMessage]:
        """Lấy tin nhắn gần đây từ DynamoDB"""
        try:
            response = self.table.query(
                KeyConditionExpression=Key('user_id').eq(user_id),
                ScanIndexForward=False,  # Mới nhất trước
                Limit=limit
            )
            items = response.get('Items', [])
            items.reverse()  # Đảo lại thứ tự cũ -> mới
            
            messages = []
            for item in items:
                # User message
                messages.append(ChatMessage(
                    role="user",
                    content=item['user_msg'],
                    timestamp=datetime.fromtimestamp(item['timestamp'])
                ))
                # AI message
                messages.append(ChatMessage(
                    role="assistant",
                    content=item['ai_msg'],
                    timestamp=datetime.fromtimestamp(item['timestamp'])
                ))
            
            return messages
        except Exception as e:
            print(f"Error querying DynamoDB: {e}")
            return []
    
    def save_message(self, user_id: str, user_msg: str, ai_msg: str) -> None:
        """Lưu tin nhắn mới vào DynamoDB"""
        timestamp = int(time.time())
        ttl = timestamp + (24 * 3600)  # Tự xóa sau 24h
        
        try:
            self.table.put_item(Item={
                'user_id': user_id,
                'timestamp': timestamp,
                'user_msg': user_msg,
                'ai_msg': ai_msg,
                'ttl': ttl
            })
        except Exception as e:
            print(f"Error saving to DynamoDB: {e}")
