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
            "Authorization": f"Bearer {self.API_TOKEN}"
        }
        self.conversation_id = "test-conversation-001"
        self.test_fact = "This is a test fact " * 100  # Create a large fact
    
    def tearDown(self):
        """Clean up after each test"""
        try:
            requests.delete(
                f"{self.BASE_URL}/facts/{self.conversation_id}",
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
            f"{self.BASE_URL}/facts/{self.conversation_id}",
            json={"fact": self.test_fact},
            headers=self.headers
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["conversation_id"], "test-conversation-001")
        self.assertEqual(data["fact"], self.test_fact)
    
    def test_create_fact_without_auth(self):
        """Test creating a fact without authentication"""
        response = requests.post(
            f"{self.BASE_URL}/facts/{self.conversation_id}",
            json={"fact": self.test_fact}
        )
        self.assertEqual(response.status_code, 403)
    
    def test_create_fact_with_invalid_token(self):
        """Test creating a fact with invalid token"""
        headers = {
            "Authorization": "Bearer invalid-token"
        }
        response = requests.post(
            f"{self.BASE_URL}/facts/{self.conversation_id}",
            json={"fact": self.test_fact},
            headers=headers
        )
        self.assertEqual(response.status_code, 401)
    
    def test_read_fact(self):
        """Test reading a fact"""
        # Create a fact first
        requests.post(
            f"{self.BASE_URL}/facts/{self.conversation_id}",
            json={"fact": self.test_fact},
            headers=self.headers
        )
        
        # Read the fact
        response = requests.get(
            f"{self.BASE_URL}/facts/{self.conversation_id}",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["conversation_id"], "test-conversation-001")
        self.assertEqual(data["fact"], self.test_fact)
    
    def test_read_nonexistent_fact(self):
        """Test reading a fact that doesn't exist"""
        response = requests.get(
            f"{self.BASE_URL}/facts/{self.conversation_id}",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
    
    def test_update_fact(self):
        """Test updating a fact"""
        # Create a fact first
        requests.post(
            f"{self.BASE_URL}/facts/{self.conversation_id}",
            json={"fact": self.test_fact},
            headers=self.headers
        )
        
        # Update the fact
        updated_fact = "Updated fact " * 100
        response = requests.put(
            f"{self.BASE_URL}/facts/{self.conversation_id}",
            json={"fact": updated_fact},
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["fact"], updated_fact)
    
    def test_update_nonexistent_fact(self):
        """Test updating a fact that doesn't exist"""
        response = requests.put(
            f"{self.BASE_URL}/facts/{self.conversation_id}",
            json={"fact": "some fact"},
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
    
    def test_delete_fact(self):
        """Test deleting a fact"""
        # Create a fact first
        requests.post(
            f"{self.BASE_URL}/facts/{self.conversation_id}",
            json={"fact": self.test_fact},
            headers=self.headers
        )
        
        # Delete the fact
        response = requests.delete(
            f"{self.BASE_URL}/facts/{self.conversation_id}",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 204)
        
        # Verify it's deleted
        response = requests.get(
            f"{self.BASE_URL}/facts/{self.conversation_id}",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
    
    def test_delete_nonexistent_fact(self):
        """Test deleting a fact that doesn't exist"""
        response = requests.delete(
            f"{self.BASE_URL}/facts/{self.conversation_id}",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
    
    def test_large_fact(self):
        """Test storing a very large fact (>8KB)"""
        # Create a fact larger than 8KB
        large_fact = "A" * 10000
        conv_id = "test-large-fact"
        headers = {
            "Authorization": f"Bearer {self.API_TOKEN}"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/facts/{conv_id}",
            json={"fact": large_fact},
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        
        # Verify we can read it back
        response = requests.get(
            f"{self.BASE_URL}/facts/{conv_id}",
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["fact"]), 10000)
        
        # Clean up
        requests.delete(f"{self.BASE_URL}/facts/{conv_id}", headers=headers)
    
    def test_list_all_facts(self):
        """Test listing all facts"""
        # Create multiple facts
        for i in range(3):
            headers = {
                "Authorization": f"Bearer {self.API_TOKEN}"
            }
            requests.post(
                f"{self.BASE_URL}/facts/test-conv-{i}",
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
                "Authorization": f"Bearer {self.API_TOKEN}"
            }
            requests.delete(f"{self.BASE_URL}/facts/test-conv-{i}", headers=headers)


class TestBudgetsAPI(unittest.TestCase):
    """Integration tests for Budgets API"""
    
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
                    print("API is ready for budget tests")
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        raise Exception("API did not become ready in time")
    
    def setUp(self):
        """Set up test fixtures"""
        self.headers = {
            "Authorization": f"Bearer {self.API_TOKEN}"
        }
        self.conversation_id = "test-budget-conversation-001"
        self.test_budget = "Item 1: Product A - $100\nItem 2: Service B - $250\n" * 100
    
    def tearDown(self):
        """Clean up after each test"""
        try:
            requests.delete(
                f"{self.BASE_URL}/budgets/{self.conversation_id}",
                headers=self.headers
            )
        except requests.exceptions.RequestException:
            pass
    
    def test_create_budget(self):
        """Test creating a new budget"""
        response = requests.post(
            f"{self.BASE_URL}/budgets/{self.conversation_id}",
            json={"budget": self.test_budget},
            headers=self.headers
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["conversation_id"], "test-budget-conversation-001")
        self.assertEqual(data["budget"], self.test_budget)
    
    def test_create_budget_without_auth(self):
        """Test creating a budget without authentication"""
        response = requests.post(
            f"{self.BASE_URL}/budgets/{self.conversation_id}",
            json={"budget": self.test_budget}
        )
        self.assertEqual(response.status_code, 403)
    
    def test_create_budget_with_invalid_token(self):
        """Test creating a budget with invalid token"""
        headers = {
            "Authorization": "Bearer invalid-token"
        }
        response = requests.post(
            f"{self.BASE_URL}/budgets/{self.conversation_id}",
            json={"budget": self.test_budget},
            headers=headers
        )
        self.assertEqual(response.status_code, 401)
    
    def test_read_budget(self):
        """Test reading a budget"""
        # Create a budget first
        requests.post(
            f"{self.BASE_URL}/budgets/{self.conversation_id}",
            json={"budget": self.test_budget},
            headers=self.headers
        )
        
        # Read the budget
        response = requests.get(
            f"{self.BASE_URL}/budgets/{self.conversation_id}",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["conversation_id"], "test-budget-conversation-001")
        self.assertEqual(data["budget"], self.test_budget)
    
    def test_read_nonexistent_budget(self):
        """Test reading a budget that doesn't exist"""
        response = requests.get(
            f"{self.BASE_URL}/budgets/{self.conversation_id}",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
    
    def test_update_budget(self):
        """Test updating a budget"""
        # Create a budget first
        requests.post(
            f"{self.BASE_URL}/budgets/{self.conversation_id}",
            json={"budget": self.test_budget},
            headers=self.headers
        )
        
        # Update the budget
        updated_budget = "Updated Item 1: New Product - $500\n" * 100
        response = requests.put(
            f"{self.BASE_URL}/budgets/{self.conversation_id}",
            json={"budget": updated_budget},
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["budget"], updated_budget)
    
    def test_update_nonexistent_budget(self):
        """Test updating a budget that doesn't exist"""
        response = requests.put(
            f"{self.BASE_URL}/budgets/{self.conversation_id}",
            json={"budget": "some budget"},
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
    
    def test_delete_budget(self):
        """Test deleting a budget"""
        # Create a budget first
        requests.post(
            f"{self.BASE_URL}/budgets/{self.conversation_id}",
            json={"budget": self.test_budget},
            headers=self.headers
        )
        
        # Delete the budget
        response = requests.delete(
            f"{self.BASE_URL}/budgets/{self.conversation_id}",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 204)
        
        # Verify it's deleted
        response = requests.get(
            f"{self.BASE_URL}/budgets/{self.conversation_id}",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
    
    def test_delete_nonexistent_budget(self):
        """Test deleting a budget that doesn't exist"""
        response = requests.delete(
            f"{self.BASE_URL}/budgets/{self.conversation_id}",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
    
    def test_large_budget(self):
        """Test storing a very large budget (>50KB)"""
        # Create a budget larger than 50KB
        large_budget = "Activity: Web Development - Price: $5,000 - Details: Full stack development\n" * 1000
        conv_id = "test-large-budget"
        headers = {
            "Authorization": f"Bearer {self.API_TOKEN}"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/budgets/{conv_id}",
            json={"budget": large_budget},
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        
        # Verify we can read it back
        response = requests.get(
            f"{self.BASE_URL}/budgets/{conv_id}",
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data["budget"]), 50000)
        
        # Clean up
        requests.delete(f"{self.BASE_URL}/budgets/{conv_id}", headers=headers)
    
    def test_list_all_budgets(self):
        """Test listing all budgets"""
        # Create multiple budgets
        for i in range(3):
            headers = {
                "Authorization": f"Bearer {self.API_TOKEN}"
            }
            requests.post(
                f"{self.BASE_URL}/budgets/test-budget-conv-{i}",
                json={"budget": f"Budget {i}: Item A - $100\nItem B - $200"},
                headers=headers
            )
        
        # List all budgets
        response = requests.get(
            f"{self.BASE_URL}/budgets/all",
            headers={"Authorization": f"Bearer {self.API_TOKEN}"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 3)
        
        # Clean up
        for i in range(3):
            headers = {
                "Authorization": f"Bearer {self.API_TOKEN}"
            }
            requests.delete(f"{self.BASE_URL}/budgets/test-budget-conv-{i}", headers=headers)


if __name__ == "__main__":
    unittest.main()
