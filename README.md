# LogiCore - Supply Chain and Logistics Management System

A comprehensive logistics management system that helps optimize supply chain operations, manage packaging materials, and locate redistribution centers.

## Features

- 📦 Smart Package Recommender
- 🌡️ Weather-based Packaging Supply Prediction
- 📍 Redistribution Center Locator
- 🗺️ Interactive Maps with Directions
- ♻️ Sustainable Packaging Solutions

## Prerequisites

### 1. Python Setup
- Python 3.8 or higher
- pip (Python package installer)

```bash
# Check Python version
python --version

# Update pip
python -m pip install --upgrade pip
```

### 2. Ollama Installation

#### Windows
1. Install WSL2 (Windows Subsystem for Linux) if not already installed:
```bash
wsl --install
```

2. Install Ollama:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### MacOS
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 3. Pull Required Models
```bash
# Pull Llama 2
ollama pull llama3.2

# Pull MXBai Embedding Model
ollama pull mxbai-embed-large
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/RiyanBhargava/LogiCore-PackageManagement
cd LogiCore-Submission
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `redistribution_center.txt` file with your centers' data in CSV format:
```csv
center_name,latitude,longitude
Center A,25.2048,55.2708
...
```

2. Ensure all API keys and configurations are set in your environment variables:
```bash
# Windows
set FLASK_APP=app.py
set FLASK_ENV=development

# Linux/MacOS
export FLASK_APP=app.py
export FLASK_ENV=development
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Access the application:
- Main application: http://localhost:8000
- Package Recommender: http://localhost:8000/package_recommender
- Package Supply Prediction: http://localhost:8000/package_supply
- Redistribution Centers: http://localhost:8000/redistribution_centers

## API Endpoints

### Package Recommender
```bash
POST /api/predict_packaging
Content-Type: application/json

{
    "product_type": "Electronics",
    "weight": 2.5,
    "fragile": true,
    "temp_condition": "Room Temperature",
    "humidity_level": "Normal"
}
```

### Find Nearest Center
```bash
POST /api/find_nearest_center
Content-Type: application/json

{
    "latitude": 25.2048,
    "longitude": 55.2708
}
```

## Development

To run the application in development mode with hot reloading:
```bash
flask run --debug --port=8000
```

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Project Structure
```
logicore/
├── app.py                         # Main Flask application
├── packaging_predictor.py         # Package recommendation logic
├── package_supply.py             # Supply prediction system
├── templates/                    # HTML templates
│   ├── index.html
│   ├── package_recommender.html
│   ├── package_supply.html
│   └── redistribution_centers.html
├── static/                      # Static files (CSS, JS)
├── tests/                       # Test files
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```


## Acknowledgments

- Ollama for local model hosting
- Folium for map integration
- All contributors and supporters
