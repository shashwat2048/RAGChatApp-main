#!/usr/bin/env python3
"""
Comprehensive test script for all RAG Chatbot API endpoints
"""
import requests
import json
import sys
import time
from typing import Dict, Any

API_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(name: str):
    """Print test header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}Testing: {name}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")

def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message: str):
    """Print info message."""
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.END}")

def test_root():
    """Test root endpoint GET /"""
    print_test("Root Endpoint (GET /)")
    try:
        response = requests.get(f"{API_URL}/")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print_success("Root endpoint working correctly")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Is it running?")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_health():
    """Test health endpoint GET /health"""
    print_test("Health Check Endpoint (GET /health)")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get("status") == "ok":
                print_success("Health check passed - API is healthy")
                if data.get("chatbot_initialized"):
                    print_success("Chatbot is initialized")
                else:
                    print_error("Chatbot is NOT initialized")
                return True
            else:
                print_error(f"Health check returned status: {data.get('status')}")
                return False
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_chat_basic():
    """Test basic chat endpoint POST /chat"""
    print_test("Chat Endpoint - Basic Query (POST /chat)")
    try:
        payload = {
            "query": "What are the key points about Chartered Accountants?",
            "use_history": False
        }
        
        print(f"Request Payload: {json.dumps(payload, indent=2)}")
        print_info("Sending request...")
        
        response = requests.post(f"{API_URL}/chat", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response received: {len(data.get('response', ''))} characters")
            print(f"Response preview: {data.get('response', '')[:300]}...")
            print_success("Chat endpoint working correctly")
            return True, data.get('response', '')
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False, None

def test_chat_with_history():
    """Test chat endpoint with history POST /chat"""
    print_test("Chat Endpoint - With History (POST /chat)")
    try:
        session_id = "test-session-123"
        
        # First query
        payload1 = {
            "query": "What is a startup?",
            "use_history": True,
            "session_id": session_id
        }
        
        print(f"First Query: {payload1['query']}")
        response1 = requests.post(f"{API_URL}/chat", json=payload1)
        print(f"Status Code: {response1.status_code}")
        
        if response1.status_code != 200:
            print_error(f"First query failed: {response1.text}")
            return False
        
        data1 = response1.json()
        print_success(f"First response received ({len(data1.get('response', ''))} chars)")
        
        # Second query (should use history)
        time.sleep(1)  # Small delay
        payload2 = {
            "query": "Tell me more about that",
            "use_history": True,
            "session_id": session_id
        }
        
        print(f"\nSecond Query: {payload2['query']}")
        response2 = requests.post(f"{API_URL}/chat", json=payload2)
        print(f"Status Code: {response2.status_code}")
        
        if response2.status_code == 200:
            data2 = response2.json()
            print_success(f"Second response received ({len(data2.get('response', ''))} chars)")
            print_success("Chat with history working correctly")
            return True
        else:
            print_error(f"Second query failed: {response2.text}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_chat_validation():
    """Test chat endpoint validation"""
    print_test("Chat Endpoint - Input Validation (POST /chat)")
    
    # Test empty query
    print_info("Testing empty query...")
    try:
        response = requests.post(f"{API_URL}/chat", json={"query": ""})
        if response.status_code == 422:  # Validation error
            print_success("Empty query correctly rejected")
        else:
            print_error(f"Expected 422, got {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    # Test missing query
    print_info("Testing missing query field...")
    try:
        response = requests.post(f"{API_URL}/chat", json={})
        if response.status_code == 422:
            print_success("Missing query correctly rejected")
        else:
            print_error(f"Expected 422, got {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    return True

def test_clear_chat():
    """Test clear chat endpoint POST /chat/clear"""
    print_test("Clear Chat Endpoint (POST /chat/clear)")
    try:
        response = requests.post(f"{API_URL}/chat/clear")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print_success("Clear chat endpoint working correctly")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_clear_session():
    """Test clear session endpoint DELETE /chat/session/{session_id}"""
    print_test("Clear Session Endpoint (DELETE /chat/session/{session_id})")
    try:
        session_id = "test-session-to-delete"
        
        # First create a session by sending a chat
        print_info(f"Creating session: {session_id}")
        requests.post(f"{API_URL}/chat", json={
            "query": "Test message",
            "session_id": session_id
        })
        
        # Now clear it
        print_info(f"Clearing session: {session_id}")
        response = requests.delete(f"{API_URL}/chat/session/{session_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print_success("Clear session endpoint working correctly")
            return True
        elif response.status_code == 404:
            print_info("Session not found (might be expected)")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_api_docs():
    """Test API documentation endpoints"""
    print_test("API Documentation Endpoints")
    
    endpoints = [
        ("/docs", "Swagger UI"),
        ("/redoc", "ReDoc"),
        ("/openapi.json", "OpenAPI Schema")
    ]
    
    all_passed = True
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{API_URL}{endpoint}")
            if response.status_code == 200:
                print_success(f"{name} ({endpoint}) is accessible")
            else:
                print_error(f"{name} ({endpoint}) returned {response.status_code}")
                all_passed = False
        except Exception as e:
            print_error(f"{name} ({endpoint}) error: {str(e)}")
            all_passed = False
    
    return all_passed

def main():
    """Run all tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}RAG Chatbot API - Comprehensive Test Suite{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    print_info(f"Testing API at: {API_URL}")
    print_info("Make sure the API is running before starting tests\n")
    
    # Wait a moment for user to read
    time.sleep(1)
    
    results = {}
    
    # Test all endpoints
    results["root"] = test_root()
    results["health"] = test_health()
    results["chat_basic"] = test_chat_basic()[0]
    results["chat_history"] = test_chat_with_history()
    results["chat_validation"] = test_chat_validation()
    results["clear_chat"] = test_clear_chat()
    results["clear_session"] = test_clear_session()
    results["api_docs"] = test_api_docs()
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Test Summary{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if result else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"{test_name:20} {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.END}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 All tests passed!{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}⚠️  Some tests failed{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())

