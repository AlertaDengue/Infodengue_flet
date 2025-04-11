# Infodengue Flet Application

A Flet-based application for visualizing dengue, zika and chikungunya data from Brazil.

## Features

- Interactive state-level choropleth maps
- City-level time series charts
- Disease selection (Dengue, Zika, Chikungunya)
- State and city search functionality
- Data caching for better performance

## Requirements

- Python 3.12+
- Flet with all dependencies (see pyproject.toml)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your-repo/Infodengue_flet.git
cd Infodengue_flet
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate on Windows
```

3. Install dependencies:
```bash
pip install -e .
```

## Running the Application

Start the application:
```bash
python main.py
```

The application will:
- Launch a local web server
- Open in your default browser
- Default to Rio de Janeiro (RJ) data

## Key Components

### Data Access
- Uses `InfodengueMaps` class from `geodata/features.py` to:
  - Connect to WFS geoserver
  - Fetch state and city boundaries
  - Get city names and codes

### Visualizations
- State maps using Matplotlib (`viz/charts.py`)
- City time series using Plotly (`viz/charts.py`)
- Interactive controls for data selection

## Configuration

You can modify:
- Default state/city in `main.py`
- Date ranges in `viz/charts.py`
- Map styles in `viz/charts.py`

## Data Sources

- Case data from [MOSQLient](https://github.com/AlertaDengue/MOSQLient)
- Geographic data from InfoDengue WFS server

## Screenshot

![App Screenshot](assets/splash.png)
