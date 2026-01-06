import unittest
import requests
import time
import os


class TestFactsAPI(unittest.TestCase):
    """Integration tests for Facts API"""
    
    BASE_URL = "http://localhost:8000"
    API_TOKEN = os.getenv("API_TOKEN", "my-secret-token")
    
    @classmethod
    def setUpClass(cls):
        """Wait for API to be ready"""
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"{cls.BASE_URL}/health", timeout=1)
                if response.status_code == 200:
                    print("API is ready")
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        raise Exception("API did not become ready in time")
    
    def setUp(self):
        """Set up test fixtures"""
        self.headers = {
            "Authorization": f"Bearer {self.API_TOKEN}",
            "X-Conversation-ID": "test-conversation-001"
        }
        self.test_fact = "This is a test fact " * 100  # Create a large fact
    
    def tearDown(self):
        """Clean up after each test"""
        try:
            requests.delete(
                f"{self.BASE_URL}/facts",
                headers=self.headers
            )
        except requests.exceptions.RequestException:
            pass
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.BASE_URL}/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})
    
    def test_create_fact(self):
        """Test creating a new fact"""
        response = requests.post(
            f"{self.BASE_URL}/facts",
            json={"fact": self.test_fact},
            headers=self.headers
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["conversation_id"], "test-conversation-001")
        self.assertEqual(data["fact"], self.test_fact)
    
    def test_create_fact_without_auth(self):
        """Test creating a fact without authentication"""
        headers = {"X-Conversation-ID": "test-conversation-001"}
        response = requests.post(
            f"{self.BASE_URL}/facts",
            json={"fact": self.test_fact},
            headers=headers
        )
        self.assertEqual(response.status_code, 403)
    
    def test_create_fact_with_invalid_token(self):
        """Test creating a fact with invalid token"""
        headers = {
            "Authorization": "Bearer invalid-token",
            "X-Conversation-ID": "test-conversation-001"
        }
        response = requests.post(
            f"{self.BASE_URL}/facts",
            json={"fact": self.test_fact},
            headers=headers
        )
        self.assertEqual(response.status_code, 401)
    
    def test_read_fact(self):
        """Test reading a fact"""
        # Create a fact first
        requests.post(
            f"{self.BASE_URL}/facts",
            json={"fact": self.test_fact},
            headers=self.headers
        )
        
        # Read the fact
        response = requests.get(
            f"{self.BASE_URL}/facts",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["conversation_id"], "test-conversation-001")
        self.assertEqual(data["fact"], self.test_fact)
    
    def test_read_nonexistent_fact(self):
        """Test reading a fact that doesn't exist"""
        response = requests.get(
            f"{self.BASE_URL}/facts",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
    
    def test_update_fact(self):
        """Test updating a fact"""
        # Create a fact first
        requests.post(
            f"{self.BASE_URL}/facts",
            json={"fact": self.test_fact},
            headers=self.headers
        )
        
        # Update the fact
        updated_fact = "Updated fact " * 100
        response = requests.put(
            f"{self.BASE_URL}/facts",
            json={"fact": updated_fact},
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["fact"], updated_fact)
    
    def test_update_nonexistent_fact(self):
        """Test updating a fact that doesn't exist"""
        response = requests.put(
            f"{self.BASE_URL}/facts",
            json={"fact": "some fact"},
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
    
    def test_delete_fact(self):
        """Test deleting a fact"""
        # Create a fact first
        requests.post(
            f"{self.BASE_URL}/facts",
            json={"fact": self.test_fact},
            headers=self.headers
        )
        
        # Delete the fact
        response = requests.delete(
            f"{self.BASE_URL}/facts",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 204)
        
        # Verify it's deleted
        response = requests.get(
            f"{self.BASE_URL}/facts",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
    
    def test_delete_nonexistent_fact(self):
        """Test deleting a fact that doesn't exist"""
        response = requests.delete(
            f"{self.BASE_URL}/facts",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
    
    def test_large_fact(self):
        """Test storing a very large fact (>8KB)"""
        # Create a fact larger than 8KB
        large_fact = "A" * 10000
        headers = {
            "Authorization": f"Bearer {self.API_TOKEN}",
            "X-Conversation-ID": "test-large-fact"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/facts",
            json={"fact": large_fact},
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        
        # Verify we can read it back
        response = requests.get(
            f"{self.BASE_URL}/facts",
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["fact"]), 10000)
        
        # Clean up
        requests.delete(f"{self.BASE_URL}/facts", headers=headers)
    
    def test_list_all_facts(self):
        """Test listing all facts"""
        # Create multiple facts
        for i in range(3):
            headers = {
                "Authorization": f"Bearer {self.API_TOKEN}",
                "X-Conversation-ID": f"test-conv-{i}"
            }
            requests.post(
                f"{self.BASE_URL}/facts",
                json={"fact": f"Fact {i}"},
                headers=headers
            )
        
        # List all facts
        response = requests.get(
            f"{self.BASE_URL}/facts/all",
            headers={"Authorization": f"Bearer {self.API_TOKEN}"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 3)
        
        # Clean up
        for i in range(3):
            headers = {
                "Authorization": f"Bearer {self.API_TOKEN}",
                "X-Conversation-ID": f"test-conv-{i}"
            }
            requests.delete(f"{self.BASE_URL}/facts", headers=headers)


if __name__ == "__main__":
    unittest.main()
