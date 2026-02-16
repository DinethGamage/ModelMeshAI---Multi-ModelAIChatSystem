"""
Test script for the Multi-Model AI Chat System.
Run this after starting the server to verify all components work correctly.
"""

import requests
import json
import time
from pathlib import Path


BASE_URL = "http://localhost:8000"
session_id = None


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_health():
    """Test health check endpoint."""
    print_section("Testing Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Health check passed")


def test_general_chat():
    """Test general conversation."""
    global session_id
    print_section("Testing General Chat")
    
    data = {
        "message": "Hello! What can you help me with?",
        "session_id": session_id
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=data)
    result = response.json()
    session_id = result["session_id"]
    
    print(f"Query: {data['message']}")
    print(f"\nResponse: {result['response']}")
    print(f"\nRouting Metadata:")
    print(json.dumps(result['routing_metadata'], indent=2))
    print(f"\n✅ General chat passed (Category: {result['routing_metadata']['route_category']})")


def test_math_query():
    """Test mathematical query with calculator."""
    global session_id
    print_section("Testing Math Query")
    
    data = {
        "message": "What is 156 * 789 + 2456?",
        "session_id": session_id
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=data)
    result = response.json()
    
    print(f"Query: {data['message']}")
    print(f"\nResponse: {result['response']}")
    print(f"\nRouting Metadata:")
    print(json.dumps(result['routing_metadata'], indent=2))
    
    metadata = result['routing_metadata']
    assert metadata['route_category'] == 'math', f"Expected 'math', got '{metadata['route_category']}'"
    print(f"\n✅ Math query passed (Calculator used: {metadata.get('calculator_used', False)})")


def test_coding_query():
    """Test coding query."""
    global session_id
    print_section("Testing Coding Query")
    
    data = {
        "message": "Write a Python function to check if a number is prime",
        "session_id": session_id
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=data)
    result = response.json()
    
    print(f"Query: {data['message']}")
    print(f"\nResponse: {result['response'][:500]}...")  # Truncate for readability
    print(f"\nRouting Metadata:")
    print(json.dumps(result['routing_metadata'], indent=2))
    
    metadata = result['routing_metadata']
    assert metadata['route_category'] == 'coding', f"Expected 'coding', got '{metadata['route_category']}'"
    print(f"\n✅ Coding query passed")


def test_session_history():
    """Test session history retrieval."""
    global session_id
    print_section("Testing Session History")
    
    response = requests.get(f"{BASE_URL}/session/{session_id}/history")
    result = response.json()
    
    print(f"Session ID: {result['session_id']}")
    print(f"Message Count: {result['message_count']}")
    print(f"Document Uploaded: {result['document_uploaded']}")
    print(f"\nConversation History:")
    for i, msg in enumerate(result['history'][-4:], 1):  # Show last 4 messages
        print(f"  {i}. [{msg['role']}]: {msg['content'][:80]}...")
    
    assert result['message_count'] >= 3, "Should have at least 3 messages"
    print(f"\n✅ Session history passed")


def test_document_query_without_upload():
    """Test document query without uploading a file."""
    global session_id
    print_section("Testing Document Query (No Upload)")
    
    data = {
        "message": "What does the document say?",
        "session_id": session_id
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=data)
    result = response.json()
    
    print(f"Query: {data['message']}")
    print(f"\nResponse: {result['response']}")
    print(f"\nRouting Metadata:")
    print(json.dumps(result['routing_metadata'], indent=2))
    
    # Should handle gracefully even without uploaded document
    print(f"\n✅ Document query without upload handled gracefully")


def test_multi_turn_context():
    """Test multi-turn conversation with context."""
    global session_id
    print_section("Testing Multi-Turn Context")
    
    # First message
    data1 = {
        "message": "My favorite color is blue",
        "session_id": session_id
    }
    response1 = requests.post(f"{BASE_URL}/chat", json=data1)
    result1 = response1.json()
    print(f"Turn 1: {data1['message']}")
    print(f"Response: {result1['response']}\n")
    
    # Follow-up that requires context
    time.sleep(1)  # Small delay
    data2 = {
        "message": "What did I just tell you about my favorite color?",
        "session_id": session_id
    }
    response2 = requests.post(f"{BASE_URL}/chat", json=data2)
    result2 = response2.json()
    print(f"Turn 2: {data2['message']}")
    print(f"Response: {result2['response']}")
    
    # Check if response mentions blue
    assert 'blue' in result2['response'].lower(), "Should remember context"
    print(f"\n✅ Multi-turn context passed")


def run_all_tests():
    """Run all test cases."""
    print("\n" + "="*60)
    print("  MULTI-MODEL AI CHAT SYSTEM - Test Suite")
    print("="*60)
    
    try:
        test_health()
        test_general_chat()
        test_math_query()
        test_coding_query()
        test_session_history()
        test_document_query_without_upload()
        test_multi_turn_context()
        
        print_section("TEST SUMMARY")
        print("✅ All tests passed successfully!")
        print(f"Session ID used: {session_id}")
        print("\nThe system is working correctly!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server.")
        print("Please ensure the server is running at http://localhost:8000")
        print("Run: python -m uvicorn app.main:app --reload")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
