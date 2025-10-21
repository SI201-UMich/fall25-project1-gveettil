import unittest
import csv
import os
from main import load_data, get_category_sales, calculate_average, find_category_seg
from collections import defaultdict

class TestCropYieldAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a test CSV file
        cls.test_file = 'test_crop_yield.csv'
        with open(cls.test_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Region', 'Soil_Type', 'Crop', 'Rainfall_mm', 'Temperature_Celsius', 
                           'Fertilizer_Used', 'Irrigation_Used', 'Weather_Condition', 
                           'Days_to_Harvest', 'Yield_tons_per_hectare'])
            writer.writerows([
                ['Region1', 'Sandy', 'Wheat', '100', '25', 'Yes', 'Yes', 'Sunny', '90', '5.5'],
                ['Region1', 'Clay', 'Rice', '200', '30', 'Yes', 'Yes', 'Rainy', '120', '4.2'],
                ['Region2', 'Sandy', 'Wheat', '150', '28', 'Yes', 'No', 'Sunny', '95', '4.8'],
                ['Region2', 'Loam', 'Corn', '180', '27', 'Yes', 'Yes', 'Cloudy', '100', '6.0']
            ])

    @classmethod
    def tearDownClass(cls):
        # Clean up test file
        if os.path.exists(cls.test_file):
            os.remove(cls.test_file)

    def test_load_data_normal(self):
        """Test 1: Normal case - file exists with data"""
        data = load_data(self.test_file)
        self.assertEqual(len(data), 4)
        self.assertTrue(isinstance(data[0], dict))

    def test_load_data_correct_keys(self):
        """Test 2: Normal case - check if all columns are loaded correctly"""
        data = load_data(self.test_file)
        expected_keys = {'Region', 'Soil_Type', 'Crop', 'Rainfall_mm', 'Temperature_Celsius',
                        'Fertilizer_Used', 'Irrigation_Used', 'Weather_Condition',
                        'Days_to_Harvest', 'Yield_tons_per_hectare'}
        self.assertEqual(set(data[0].keys()), expected_keys)

    def test_load_data_nonexistent_file(self):
        """Test 3: Edge case - nonexistent file"""
        with self.assertRaises(FileNotFoundError):
            load_data('nonexistent.csv')

    def test_load_data_empty_file(self):
        """Test 4: Edge case - empty file"""
        empty_file = 'empty.csv'
        with open(empty_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Region', 'Crop', 'Yield_tons_per_hectare'])  # Only header
        data = load_data(empty_file)
        self.assertEqual(len(data), 0)
        os.remove(empty_file)

    def test_get_category_sales_normal(self):
        """Test 1: Normal case - multiple crops"""
        data = load_data(self.test_file)
        result = get_category_sales(data)
        self.assertEqual(len(result), 3)  # Wheat, Rice, Corn
        self.assertTrue(all(isinstance(yields, list) for yields in result.values()))

    def test_get_category_sales_values(self):
        """Test 2: Normal case - check specific values"""
        data = load_data(self.test_file)
        result = get_category_sales(data)
        wheat_yields = result['Wheat']
        self.assertEqual(len(wheat_yields), 2)
        self.assertIn(5.5, wheat_yields)
        self.assertIn(4.8, wheat_yields)

    def test_get_category_sales_empty_data(self):
        """Test 3: Edge case - empty dataset"""
        result = get_category_sales([])
        self.assertEqual(len(result), 0)

    def test_get_category_sales_missing_values(self):
        """Test 4: Edge case - missing yield values"""
        data = [{'Crop': 'Wheat', 'Yield_tons_per_hectare': ''},
                {'Crop': 'Wheat', 'Yield_tons_per_hectare': '5.0'}]
        with self.assertRaises(ValueError):
            get_category_sales(data)

    def test_calculate_average_normal(self):
        """Test 1: Normal case - multiple values"""
        category_sales = {'Wheat': [5.5, 4.8], 'Rice': [4.2]}
        result = calculate_average(category_sales)
        self.assertAlmostEqual(result['Wheat'], 5.15)
        self.assertAlmostEqual(result['Rice'], 4.2)

    def test_calculate_average_single_value(self):
        """Test 2: Normal case - single value per category"""
        category_sales = {'Corn': [6.0]}
        result = calculate_average(category_sales)
        self.assertEqual(result['Corn'], 6.0)

    def test_calculate_average_empty_dict(self):
        """Test 3: Edge case - empty dictionary"""
        result = calculate_average({})
        self.assertEqual(result, {})

    def test_calculate_average_empty_list(self):
        """Test 4: Edge case - category with empty list"""
        category_sales = {'Wheat': []}
        with self.assertRaises(ZeroDivisionError):
            calculate_average(category_sales)

    def test_find_category_seg_normal(self):
        """Test 1: Normal case - multiple regions"""
        data = load_data(self.test_file)
        result = find_category_seg(data)
        self.assertEqual(len(result), 2)  # Two regions
        self.assertTrue(all(isinstance(crop, str) for crop in result.values()))

    def test_find_category_seg_specific_region(self):
        """Test 2: Normal case - check specific region"""
        data = load_data(self.test_file)
        result = find_category_seg(data)
        self.assertEqual(result['Region1'], 'Wheat')  # Most frequent in Region1

    def test_find_category_seg_empty_data(self):
        """Test 3: Edge case - empty dataset"""
        result = find_category_seg([])
        self.assertEqual(len(result), 0)

    def test_find_category_seg_tie(self):
        """Test 4: Edge case - tie in frequency"""
        data = [
            {'Region': 'R1', 'Crop': 'Wheat'},
            {'Region': 'R1', 'Crop': 'Rice'},
        ]
        result = find_category_seg(data)
        self.assertTrue(result['R1'] in ['Wheat', 'Rice'])

if __name__ == '__main__':
    unittest.main()