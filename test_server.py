import unittest
from unittest.mock import patch, MagicMock
import json
from server import app

class TestTerraMindServer(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        self.client = app.test_client()

    @patch('database.get_user')
    def test_get_user_profile(self, mock_get_user):
        # Mock user data
        mock_user = {
            "id": 1,
            "username": "Test Explorer",
            "email": "test@terramind.eco",
            "carbon_score": 80,
            "xp": 20000,
            "level": 20,
            "credits": 3000,
            "trees": 5
        }
        mock_get_user.return_value = mock_user

        response = self.client.get('/api/user')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], "Test Explorer")
        self.assertEqual(data['credits'], 3000)
        mock_get_user.assert_called_once_with(user_id=1)

    @patch('database.get_carbon_logs')
    @patch('database.get_user')
    def test_get_dashboard_summary(self, mock_get_user, mock_get_carbon_logs):
        mock_user = {"id": 1, "username": "Test Explorer"}
        mock_logs = [
            {
                "id": 101,
                "user_id": 1,
                "date": "2026-06-12",
                "public_transport": 20,
                "renewable_energy": 10,
                "diet": "Omnivore",
                "commuting_mode": "Gas Car",
                "transport_emissions": 2.5,
                "energy_emissions": 1.8,
                "diet_emissions": 1.2,
                "total_emissions": 5.5
            }
        ]
        mock_get_user.return_value = mock_user
        mock_get_carbon_logs.return_value = mock_logs

        response = self.client.get('/api/dashboard/summary')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['user']['username'], "Test Explorer")
        self.assertEqual(len(data['history']), 1)
        self.assertEqual(data['latest_log']['total_emissions'], 5.5)

    @patch('database.get_user')
    @patch('database.add_carbon_log')
    def test_log_carbon_calculator_valid(self, mock_add_carbon_log, mock_get_user):
        payload = {
            "public_transport": 80,
            "renewable_energy": 50,
            "diet": "Veggie",
            "commuting_mode": "Electric"
        }
        mock_add_carbon_log.return_value = {"id": 102, "total_emissions": 2.5}
        mock_get_user.return_value = {"id": 1, "carbon_score": 85}

        response = self.client.post(
            '/api/calculator/log',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['log']['total_emissions'], 2.5)
        mock_add_carbon_log.assert_called_once_with(user_id=1, log_data=payload)

    def test_log_carbon_calculator_invalid_payload(self):
        response = self.client.post(
            '/api/calculator/log',
            data=json.dumps(None),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_log_carbon_calculator_invalid_ranges(self):
        # We test real database layer logic since we are not patching database.add_carbon_log
        # or we mock it throwing ValueError. Let's test with the actual database module imported,
        # but with mock client.
        
        # Test out of range public transport
        payload = {
            "public_transport": 150,
            "renewable_energy": 50,
            "diet": "Veggie",
            "commuting_mode": "Electric"
        }
        response = self.client.post(
            '/api/calculator/log',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Public transport percentage must be between 0 and 100", data['error'])

        # Test negative renewable energy
        payload = {
            "public_transport": 50,
            "renewable_energy": -10,
            "diet": "Veggie",
            "commuting_mode": "Electric"
        }
        response = self.client.post(
            '/api/calculator/log',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Renewable energy percentage must be between 0 and 100", data['error'])

        # Test invalid diet
        payload = {
            "public_transport": 50,
            "renewable_energy": 50,
            "diet": "Keto",
            "commuting_mode": "Electric"
        }
        response = self.client.post(
            '/api/calculator/log',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Invalid diet choice", data['error'])

    @patch('database.add_transaction')
    def test_redeem_marketplace_voucher_valid(self, mock_add_transaction):
        payload = {
            "item_title": "Eco Thermostat",
            "cost_credits": 1500
        }
        mock_add_transaction.return_value = {
            "success": True,
            "credits": 2000,
            "transaction": {"id": 3, "item_title": "Eco Thermostat", "cost_credits": 1500}
        }

        response = self.client.post(
            '/api/marketplace/redeem',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['credits'], 2000)

    def test_redeem_marketplace_voucher_invalid_inputs(self):
        # Negative credits exploit
        payload = {
            "item_title": "Eco Thermostat",
            "cost_credits": -5000
        }
        response = self.client.post(
            '/api/marketplace/redeem',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Credit cost must be greater than zero", data['error'])

        # Cost non-integer
        payload = {
            "item_title": "Eco Thermostat",
            "cost_credits": "abc"
        }
        response = self.client.post(
            '/api/marketplace/redeem',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Credit cost must be an integer", data['error'])

        # Empty/missing title
        payload = {
            "cost_credits": 100
        }
        response = self.client.post(
            '/api/marketplace/redeem',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Item title and credit cost required", data['error'])

    @patch('database.get_user')
    def test_redeem_insufficient_credits(self, mock_get_user):
        # Test actual database transaction logic with insufficient credits
        mock_user = {
            "id": 1,
            "credits": 200
        }
        mock_get_user.return_value = mock_user

        payload = {
            "item_title": "Solar Cooker",
            "cost_credits": 1000
        }
        response = self.client.post(
            '/api/marketplace/redeem',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Insufficient credits")

if __name__ == '__main__':
    unittest.main()
