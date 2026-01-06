#!/usr/bin/env python3
"""
Simple test script for RAG Chatbot API
"""
import requests
import json
import sys

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_chat(query: str, session_id: str = None):
    """Test chat endpoint."""
    print(f"\nTesting chat endpoint with query: '{query}'...")
    try:
        payload = {
            "query": query,
            "use_history": True
        }
        if session_id:
            payload["session_id"] = session_id
        
        response = requests.post(f"{API_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['response'][:200]}...")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run tests."""
    print("=" * 50)
    print("RAG Chatbot API Test Script")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("\n❌ Health check failed. Is the API running?")
        sys.exit(1)
    
    print("\n✅ Health check passed!")
    
    # Test chat
    test_queries = [
        "What are the key points about Chartered Accountants?",
        "Tell me about startup funding strategies"
    ]
    
    session_id = "test-session-123"
    
    for query in test_queries:
        if not test_chat(query, session_id):
            print(f"\n❌ Chat test failed for query: {query}")
            sys.exit(1)
        print("✅ Chat test passed!")
    
    print("\n" + "=" * 50)
    print("All tests passed! 🎉")
    print("=" * 50)

if __name__ == "__main__":
    main()

