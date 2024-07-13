import unittest
import json
from app import app, calculate_mpg, calculate_total_fuel, calculate_predicted_mpg

class FuelTrackerTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_add_entry(self):
        response = self.app.post('/add', data={
            'date': '',
            'odometer': 1000,
            'fuel_price': 1.345,
            'fuel': 40
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('date', data)
        self.assertEqual(data['odometer'], 1000)
        self.assertAlmostEqual(data['fuel_price'], 1.345, places=3)
        self.assertEqual(data['fuel'], 40)
        self.assertAlmostEqual(data['total_fuel_price'], 1.345 * 40, places=3)

    def test_calculate_mpg(self):
        last_entry = {'odometer': 900, 'fuel': 30}
        new_entry = {'odometer': 1000, 'fuel': 40}
        mpg = calculate_mpg(last_entry, new_entry)
        self.assertAlmostEqual(mpg, 9.4635, places=2)

    def test_calculate_total_fuel(self):
        data = [
            {'fuel': 40},
            {'fuel': 30},
        ]
        total_fuel = calculate_total_fuel(data)
        self.assertEqual(total_fuel, 70)

    def test_calculate_predicted_mpg(self):
        data = [
            {'odometer': 900, 'fuel': 30},
            {'odometer': 1000, 'fuel': 40},
            {'odometer': 1100, 'fuel': 35},
        ]
        predicted_mpg = calculate_predicted_mpg(data)
        self.assertAlmostEqual(predicted_mpg, 10.0944, places=2)

    def test_export_data(self):
        response = self.app.get('/export')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)
        with open('data.csv', 'rb') as f:
            self.assertTrue(f.read())

if __name__ == '__main__':
    unittest.main()
