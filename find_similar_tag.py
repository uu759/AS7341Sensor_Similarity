import pandas as pd
import numpy as np

def euclidean_distance(row1, row2):
    return np.sqrt(np.sum((row1 - row2)**2))

def find_similar_tag(new_sensor_data, csv_file='sensor_data.csv'):
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found. Please ensure it exists and contains sensor data.")
        return None

    # Assuming the first column is 'tag' and the rest are sensor features
    tags = df['tag']
    sensor_features = df.drop(columns=['tag'])

    # Convert new_sensor_data to a numpy array for calculation
    new_sensor_array = np.array(new_sensor_data)

    min_distance = float('inf')
    most_similar_tag = None

    for index, row in sensor_features.iterrows():
        distance = euclidean_distance(row.values, new_sensor_array)
        if distance < min_distance:
            min_distance = distance
            most_similar_tag = tags.iloc[index]

    return most_similar_tag, min_distance

if __name__ == "__main__":
    print("Enter new sensor data (comma-separated values for f1,f2,...,f8,vis,ir,clear):")
    input_str = input()
    try:
        new_data = [float(x.strip()) for x in input_str.split(',')]
        if len(new_data) != 11: # f1-f8 (8) + vis (1) + ir (1) + clear (1) = 11
            print("Error: Please enter exactly 11 comma-separated sensor values.")
        else:
            similar_tag, distance = find_similar_tag(new_data, 'C:/Users/sky27/OneDrive/바탕 화면/Arduino/AS7341_test/AS7341_test/sensor_data.csv')
            if similar_tag:
                print(f"The most similar tag is: {similar_tag} (Distance: {distance:.2f})")
    except ValueError:
        print("Error: Invalid input. Please enter numeric values separated by commas.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
