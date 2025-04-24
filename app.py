from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from datetime import datetime
import folium
import numpy as np
from packaging_predictor import PackagingPredictor
from package_supply import WeatherBasedPackaging
import os

app = Flask(__name__)

# Initialize predictors
packaging_predictor = PackagingPredictor()
weather_packaging = WeatherBasedPackaging()

# Load redistribution centers data
df = pd.read_csv('redistribution_center.txt')

def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r

def find_nearest_center(user_lat, user_lon, centers_df):
    distances = centers_df.apply(
        lambda row: haversine_distance(user_lat, user_lon, row['latitude'], row['longitude']),
        axis=1
    )
    nearest_idx = distances.idxmin()
    return centers_df.iloc[nearest_idx]

def create_map(user_location, nearest_center):
    # Create a map centered on Dubai
    dubai_map = folium.Map(location=[25.2048, 55.2708], zoom_start=11)
    
    # Add markers for all redistribution centers
    for idx, center in df.iterrows():
        # Determine if this is the nearest center
        is_nearest = center['center_name'] == nearest_center['center_name']
        
        # Choose color and icon based on whether it's the nearest center
        color = 'red' if is_nearest else 'gray'
        icon_type = 'info-sign' if is_nearest else 'home'
        
        folium.Marker(
            location=[center['latitude'], center['longitude']],
            popup=center['center_name'],
            icon=folium.Icon(color=color, icon=icon_type)
        ).add_to(dubai_map)
    
    # Add marker for user location
    folium.Marker(
        location=user_location,
        popup='Your Location',
        icon=folium.Icon(color='blue', icon='user')
    ).add_to(dubai_map)
    
    # Draw line between user and nearest center
    folium.PolyLine(
        locations=[
            user_location,
            [nearest_center['latitude'], nearest_center['longitude']]
        ],
        weight=2,
        color='green',
        opacity=0.8
    ).add_to(dubai_map)
    
    return dubai_map

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/package_recommender')
def package_recommender():
    return render_template('package_recommender.html')

@app.route('/package_supply')
def package_supply():
    return render_template('package_supply.html')

@app.route('/redistribution_centers')
def redistribution_centers_page():
    return render_template('redistribution_centers.html')

# Package Recommender API
@app.route('/api/predict_packaging', methods=['POST'])
def predict_packaging():
    try:
        data = request.json
        test_data = {
            'Product_Type': data['product_type'],
            'Weight_kg': float(data['weight']),
            'Fragile': data['fragile'],
            'Temp_Condition': data['temp_condition'],
            'Humidity_Level': data['humidity_level']
        }
        
        result = packaging_predictor.predict(test_data)
        return jsonify({'result': result['result']})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Test Package API
@app.route('/api/predict_test_package', methods=['GET'])
def predict_test_package():
    try:
        # Load test data
        test_df = pd.read_csv("test_package.csv")
        test_data = test_df.iloc[0]
        
        # Make prediction
        result = packaging_predictor.predict(test_data)
        
        # Format the result
        formatted_result = f"""
        Product Details:
        Product ID: {test_data['Product_ID']}
        Product Type: {test_data['Product_Type']}
        Weight: {test_data['Weight_kg']} kg
        Fragile: {test_data['Fragile']}
        Temperature Condition: {test_data['Temp_Condition']}
        Humidity Level: {test_data['Humidity_Level']}
        
        Prediction and Reasoning:
        {result['result']}
        """
        
        return jsonify({'result': formatted_result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Package Supply API
@app.route('/api/generate_packaging_list', methods=['GET'])
def generate_packaging_list():
    try:
        # Get weather data
        df, next_4_months, next_month_names = weather_packaging.get_weather_data()
        
        # Generate packaging list
        packaging_list = weather_packaging.generate_packaging_list(df, next_4_months, next_month_names)
        
        # Send email
        weather_packaging.send_email(packaging_list)
        
        # Prepare weather data for frontend
        weather_data = []
        for idx in next_4_months:
            weather_data.append({
                'month': df.iloc[idx]['month'],
                'weather': df.iloc[idx]['weather']
            })
        
        return jsonify({
            'status': 'success',
            'message': 'Packaging list generated and email sent successfully',
            'weather_data': weather_data,
            'packaging_list': packaging_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Redistribution Centers API
@app.route('/api/find_nearest_center', methods=['POST'])
def api_find_nearest_center():
    try:
        data = request.json
        user_lat = float(data['latitude'])
        user_lon = float(data['longitude'])
        
        user_location = (user_lat, user_lon)
        nearest = find_nearest_center(user_lat, user_lon, df)
        
        # Create the map
        dubai_map = create_map(user_location, nearest)
        map_html = dubai_map._repr_html_()
        
        # Create Google Maps directions URL
        google_maps_url = f"https://www.google.com/maps/dir/{user_lat},{user_lon}/{nearest['latitude']},{nearest['longitude']}"
        
        result = {
            'nearest_center': nearest['center_name'],
            'center_coordinates': [nearest['latitude'], nearest['longitude']],
            'distance': haversine_distance(user_lat, user_lon, nearest['latitude'], nearest['longitude']),
            'map_html': map_html,
            'directions_url': google_maps_url
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True,port=8001) 