import unittest
import json
from app import app, calculate_mpg

class FuelTrackerTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_add_entry(self):
        response = self.app.post('/add', data={
            'odometer': 1000,
            'fuel_price': 1.23,
            'fuel': 40
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('date', data)
        self.assertEqual(data['odometer'], 1000)
        self.assertEqual(data['fuel_price'], 1.23)
        self.assertEqual(data['fuel'], 40)

    def test_calculate_mpg(self):
        last_entry = {'odometer': 900, 'fuel': 30}
        new_entry = {'odometer': 1000, 'fuel': 40}
        mpg = calculate_mpg(last_entry, new_entry)
        self.assertAlmostEqual(mpg, 9.4635, places=2)

    def test_export_data(self):
        response = self.app.get('/export')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)
        with open('data.csv', 'rb') as f:
            self.assertTrue(f.read())

if __name__ == '__main__':
    unittest.main()
