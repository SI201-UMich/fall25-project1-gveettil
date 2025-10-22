import csv
import unittest
import os

def load_data(file_path):
    
    data = []
    with open(file_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data

def group_yields_by_crop(data):
    """
    Group yield values by crop name
    """
    crop_yields = {}
    for row in data:
        yield_value = float(row['Yield_tons_per_hectare'])
        crop = row['Crop']
        if crop not in crop_yields:
            crop_yields[crop] = []
        crop_yields[crop].append(yield_value)
    return crop_yields

def calculate_average_yield(data):
    """
    Group yields by crop and calculate average yield for each crop
    """
    crop_yields = group_yields_by_crop(data)
    averages = {}
    for crop, yields in crop_yields.items():
        averages[crop] = sum(yields) / len(yields)
    return averages

def most_frequent_crop_by_region(data):
    """
    Find the most frequent crop for each region
    """
    region_crops = {}
    for row in data:
        region = row['Region']
        crop = row['Crop']
        if region not in region_crops:
            region_crops[region] = {}
        if crop not in region_crops[region]:
            region_crops[region][crop] = 0
        region_crops[region][crop] += 1
    result = {}
    for region, crops in region_crops.items():
        result[region] = max(crops.items(), key=lambda x: x[1])[0]
    return result

def main():

    # Load data
    file_path = 'crop_yield.csv'
    data = load_data(file_path)
    
    # Calculate average yields for each crop
    average_yields = calculate_average_yield(data)
    
    # Find most frequent crop per region
    region_crops = most_frequent_crop_by_region(data)
    
    # Write results to files
    with open('average_yield_results.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Crop', 'Average Yield (tons/hectare)'])
        for crop, avg_yield in average_yields.items():
            writer.writerow([crop, f"{avg_yield:.2f}"])

    with open('most_common_crops_by_region.txt', 'w') as file:
        file.write("Most Frequent Crop by Region:\n\n")
        for region, crop in region_crops.items():
            file.write(f"Region: {region}\n")
            file.write(f"Most Common Crop: {crop}\n\n")

class TestCropYieldAnalysis(unittest.TestCase):
    def setUp(self):
        # Create a test CSV file before each test
        self.test_file = 'test_crop_yield.csv'
        with open(self.test_file, 'w', newline='') as file:
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

    def test_group_yields_by_crop_normal(self):
        """Test 1: Normal case - multiple crops"""
        data = load_data(self.test_file)
        result = group_yields_by_crop(data)
        self.assertEqual(len(result), 3)  # Wheat, Rice, Corn
        self.assertTrue(all(isinstance(yields, list) for yields in result.values()))

    def test_group_yields_by_crop_values(self):
        """Test 2: Normal case - check specific values"""
        data = load_data(self.test_file)
        result = group_yields_by_crop(data)
        wheat_yields = result['Wheat']
        self.assertEqual(len(wheat_yields), 2)
        self.assertIn(5.5, wheat_yields)
        self.assertIn(4.8, wheat_yields)

    def test_group_yields_by_crop_empty_data(self):
        """Test 3: Edge case - empty dataset"""
        result = group_yields_by_crop([])
        self.assertEqual(len(result), 0)

    def test_group_yields_by_crop_missing_values(self):
        """Test 4: Edge case - missing yield values"""
        data = [{'Crop': 'Wheat', 'Yield_tons_per_hectare': ''},
                {'Crop': 'Wheat', 'Yield_tons_per_hectare': '5.0'}]
        with self.assertRaises(ValueError):
            group_yields_by_crop(data)

    def test_calculate_average_yield_normal(self):
        """Test 1: Normal case - multiple values"""
        data = [
            {'Crop': 'Wheat', 'Yield_tons_per_hectare': '5.5'},
            {'Crop': 'Wheat', 'Yield_tons_per_hectare': '4.8'},
            {'Crop': 'Rice', 'Yield_tons_per_hectare': '4.2'}
        ]
        result = calculate_average_yield(data)
        self.assertAlmostEqual(result['Wheat'], 5.15)
        self.assertAlmostEqual(result['Rice'], 4.2)

    def test_calculate_average_yield_single_value(self):
        """Test 2: Normal case - single value per crop"""
        data = [
            {'Crop': 'Corn', 'Yield_tons_per_hectare': '6.0'}
        ]
        result = calculate_average_yield(data)
        self.assertEqual(result['Corn'], 6.0)

    def test_calculate_average_yield_empty_dict(self):
        """Test 3: Edge case - empty dictionary"""
        result = calculate_average_yield([])
        self.assertEqual(result, {})

    def test_calculate_average_yield_empty_list(self):
        """Test 4: Edge case - crop with empty list"""
        data = [
            {'Crop': 'Wheat', 'Yield_tons_per_hectare': ''}
        ]
        with self.assertRaises(ValueError):
            calculate_average_yield(data)

    def test_most_frequent_crop_by_region_normal(self):
        """Test 1: Normal case - multiple regions"""
        data = load_data(self.test_file)
        result = most_frequent_crop_by_region(data)
        self.assertEqual(len(result), 2)  # Two regions
        self.assertTrue(all(isinstance(crop, str) for crop in result.values()))

    def test_most_frequent_crop_by_region_specific_region(self):
        """Test 2: Normal case - check specific region"""
        data = load_data(self.test_file)
        result = most_frequent_crop_by_region(data)
        self.assertEqual(result['Region1'], 'Wheat')  # Most frequent in Region1

    def test_most_frequent_crop_by_region_empty_data(self):
        """Test 3: Edge case - empty dataset"""
        result = most_frequent_crop_by_region([])
        self.assertEqual(len(result), 0)

    def test_most_frequent_crop_by_region_tie(self):
        """Test 4: Edge case - tie in frequency"""
        data = [
            {'Region': 'R1', 'Crop': 'Wheat'},
            {'Region': 'R1', 'Crop': 'Rice'},
        ]
        result = most_frequent_crop_by_region(data)
        self.assertTrue(result['R1'] in ['Wheat', 'Rice'])

if __name__ == "__main__":
    # First run the tests
    import unittest
    import os
    unittest.main(argv=[''], exit=False)
    
    # Then run the main program
    print("\nRunning main program...")
    main()