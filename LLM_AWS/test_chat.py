"""
Test script để test chat API
"""
import requests
import jwt
import json
from datetime import datetime, timedelta


# Configuration
API_URL = "http://localhost:7000/api/chat/"
JWT_SECRET = "MY_SUPER_SECRET_KEY_1234567890ABCDEF"
USER_ID = "test_user_123"
SESSION_ID = "test_session_001"


def create_test_jwt(user_id: str) -> str:
    """Tạo JWT token để test"""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


def chat(message: str, session_id: str = SESSION_ID):
    """Gửi message đến chat API"""
    token = create_test_jwt(USER_ID)
    
    headers = {
        "Content-Type": "application/json",
        "X-User-Authorization": f"Bearer {token}"
    }
    
    data = {
        "session_id": session_id,
        "message": message
    }
    
    print(f"\n{'='*60}")
    print(f"🗣️  User: {message}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"\n🤖 AI: {result['message']}")
        print(f"\n📊 Metadata:")
        print(f"   - Used Short Memory: {result['used_short_memory']}")
        print(f"   - Used Long Memory: {result['used_long_memory']}")
        print(f"   - Used Vector DB: {result['used_vector_db']}")
        
        if result['sources']:
            print(f"\n📚 Sources:")
            for source in result['sources']:
                print(f"   - {source}")
        
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🚀 AI Chat API Test Script")
    print("="*60)
    
    # Test 1: First message
    print("\n\n📝 Test 1: First message (no memory)")
    chat("Hello! My name is John and I love football.")
    
    # Test 2: Follow-up (should use short memory)
    print("\n\n📝 Test 2: Follow-up question (should use short memory)")
    chat("What's my name?")
    
    # Test 3: NFL question (should use vector DB)
    print("\n\n📝 Test 3: NFL question (should use vector DB)")
    chat("Tell me about the NFL")
    
    # Test 4: Complex question (should use all memories)
    print("\n\n📝 Test 4: Complex question (should use all sources)")
    chat("Based on what we discussed, what do you know about me and football?")
    
    print("\n\n" + "="*60)
    print("✅ Test completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
