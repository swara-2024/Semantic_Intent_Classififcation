#!/usr/bin/env python3
# test_api.py - API Testing & Demo Script

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

class APITester:
    """Test suite for Semantic Intent Classification API"""
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session_ids = {}
    
    def print_response(self, title, response):
        """Pretty print API response"""
        print(f"\n{'='*60}")
        print(f"TEST: {title}")
        print(f"{'='*60}")
        print(f"Status: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    # ==================== Health Checks ====================
    
    def test_health(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.base_url}/health")
        self.print_response("Health Check", response)
        return response.status_code == 200
    
    # ==================== Chat Tests ====================
    
    def test_chat_demo_request(self):
        """Test chat with demo request"""
        payload = {
            "query": "I want to schedule a demo",
            "user_id": "user_demo_1"
        }
        response = requests.post(f"{self.base_url}/api/chat", json=payload)
        self.print_response("Chat - Demo Request", response)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('flow_data'):
                self.session_ids['demo'] = result['flow_data']['session_id']
        
        return response.status_code == 200
    
    def test_chat_pricing_inquiry(self):
        """Test chat with pricing inquiry"""
        payload = {
            "query": "How much does your service cost?",
            "user_id": "user_pricing_1"
        }
        response = requests.post(f"{self.base_url}/api/chat", json=payload)
        self.print_response("Chat - Pricing Inquiry", response)
        return response.status_code == 200
    
    def test_chat_support_request(self):
        """Test chat with support request"""
        payload = {
            "query": "I'm having issues with the platform",
            "user_id": "user_support_1"
        }
        response = requests.post(f"{self.base_url}/api/chat", json=payload)
        self.print_response("Chat - Support Request", response)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('flow_data'):
                self.session_ids['support'] = result['flow_data']['session_id']
        
        return response.status_code == 200
    
    def test_chat_invalid_request(self):
        """Test chat with invalid request"""
        payload = {"no_query_field": "test"}
        response = requests.post(f"{self.base_url}/api/chat", json=payload)
        self.print_response("Chat - Invalid Request (should fail)", response)
        return response.status_code == 400
    
    # ==================== Flow Tests ====================
    
    def test_start_flow(self):
        """Test starting a flow"""
        payload = {
            "intent": "demo_request",
            "user_id": "user_flow_test"
        }
        response = requests.post(f"{self.base_url}/api/flow/start", json=payload)
        self.print_response("Flow - Start Demo Booking", response)
        
        if response.status_code == 200:
            result = response.json()
            self.session_ids['flow_test'] = result.get('session_id')
        
        return response.status_code == 200
    
    def test_flow_respond(self):
        """Test responding to a flow question"""
        if 'flow_test' not in self.session_ids:
            print("Skipping: flow_test session not found. Run test_start_flow first.")
            return False
        
        payload = {
            "session_id": self.session_ids['flow_test'],
            "response": "John Doe"
        }
        response = requests.post(f"{self.base_url}/api/flow/respond", json=payload)
        self.print_response("Flow - Respond with Name", response)
        return response.status_code == 200
    
    def test_flow_respond_invalid_email(self):
        """Test responding with invalid email"""
        if 'flow_test' not in self.session_ids:
            print("Skipping: flow_test session not found.")
            return False
        
        payload = {
            "session_id": self.session_ids['flow_test'],
            "response": "not-an-email"
        }
        response = requests.post(f"{self.base_url}/api/flow/respond", json=payload)
        self.print_response("Flow - Invalid Email Response (should fail)", response)
        return response.status_code == 400
    
    def test_flow_respond_valid_email(self):
        """Test responding with valid email"""
        if 'flow_test' not in self.session_ids:
            print("Skipping: flow_test session not found.")
            return False
        
        payload = {
            "session_id": self.session_ids['flow_test'],
            "response": "john@example.com"
        }
        response = requests.post(f"{self.base_url}/api/flow/respond", json=payload)
        self.print_response("Flow - Valid Email Response", response)
        return response.status_code == 200
    
    def test_get_session(self):
        """Test getting session data"""
        if 'flow_test' not in self.session_ids:
            print("Skipping: flow_test session not found.")
            return False
        
        session_id = self.session_ids['flow_test']
        response = requests.get(f"{self.base_url}/api/flow/session/{session_id}")
        self.print_response("Flow - Get Session Data", response)
        return response.status_code == 200
    
    def test_cancel_flow(self):
        """Test cancelling a flow"""
        if 'flow_test' not in self.session_ids:
            print("Skipping: flow_test session not found.")
            return False
        
        session_id = self.session_ids['flow_test']
        response = requests.post(f"{self.base_url}/api/flow/cancel/{session_id}")
        self.print_response("Flow - Cancel Session", response)
        return response.status_code == 200
    
    # ==================== Information Tests ====================
    
    def test_available_flows(self):
        """Test getting available flows"""
        response = requests.get(f"{self.base_url}/api/flows/available")
        self.print_response("Info - Available Flows", response)
        return response.status_code == 200
    
    def test_intents_with_flows(self):
        """Test getting intents with flows"""
        response = requests.get(f"{self.base_url}/api/intents/with-flows")
        self.print_response("Info - Intents with Flows", response)
        return response.status_code == 200
    
    # ==================== Analysis Tests ====================
    
    def test_analyze_query(self):
        """Test query analysis"""
        payload = {
            "query": "I need a demo of your pricing and features"
        }
        response = requests.post(f"{self.base_url}/api/analyze/query", json=payload)
        self.print_response("Analysis - Query Characteristics", response)
        return response.status_code == 200
    
    def test_analyze_simple_query(self):
        """Test analyzing a simple query"""
        payload = {
            "query": "help"
        }
        response = requests.post(f"{self.base_url}/api/analyze/query", json=payload)
        self.print_response("Analysis - Simple Query", response)
        return response.status_code == 200
    
    # ==================== Test Runner ====================
    
    def run_all_tests(self):
        """Run all tests and report results"""
        tests = [
            ("Health Check", self.test_health),
            ("Chat - Demo Request", self.test_chat_demo_request),
            ("Chat - Pricing Inquiry", self.test_chat_pricing_inquiry),
            ("Chat - Support Request", self.test_chat_support_request),
            ("Chat - Invalid Request", self.test_chat_invalid_request),
            ("Flow - Start", self.test_start_flow),
            ("Flow - Respond", self.test_flow_respond),
            ("Flow - Invalid Email", self.test_flow_respond_invalid_email),
            ("Flow - Valid Email", self.test_flow_respond_valid_email),
            ("Flow - Get Session", self.test_get_session),
            ("Flow - Cancel", self.test_cancel_flow),
            ("Info - Available Flows", self.test_available_flows),
            ("Info - Intents with Flows", self.test_intents_with_flows),
            ("Analysis - Query", self.test_analyze_query),
            ("Analysis - Simple Query", self.test_analyze_simple_query),
        ]
        
        results = {}
        print("\n" + "="*60)
        print("STARTING API TEST SUITE")
        print("="*60)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = "PASS" if result else "FAIL"
            except Exception as e:
                print(f"ERROR in {test_name}: {e}")
                results[test_name] = "ERROR"
        
        # Print summary
        self.print_summary(results)
    
    def print_summary(self, results):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for v in results.values() if v == "PASS")
        failed = sum(1 for v in results.values() if v == "FAIL")
        errors = sum(1 for v in results.values() if v == "ERROR")
        total = len(results)
        
        for test_name, result in results.items():
            status_symbol = "✓" if result == "PASS" else "✗" if result == "FAIL" else "!"
            print(f"{status_symbol} {test_name}: {result}")
        
        print(f"\n{'='*60}")
        print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Errors: {errors}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    import sys
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   Semantic Intent Classification - API Test Suite         ║
    ║   Testing all REST endpoints and business logic           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("ERROR: API server returned non-200 status. Is it running?")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Cannot connect to API at {BASE_URL}")
        print("Make sure the Flask server is running:")
        print(f"  python flow_api.py")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    # Run tests
    tester = APITester()
    tester.run_all_tests()
