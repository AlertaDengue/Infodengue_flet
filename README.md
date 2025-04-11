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

2. Install uv
On Mac and Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
On windows:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```



3Create and activate a virtual environment:
```bash
uv sync 
```



## Running the Application

Start the application:
```bash
uv run flet run main.py
```

The application will:
- Launch the desktop application
- Default to Rio de Janeiro data
- You can select other states and cities using the dropdown menus

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

- Case data through the [MOSQLient library](https://github.com/mosqlimate-project/mosqlient)
- Geographic data from InfoDengue WFS server

## Screenshot

![App Screenshot](assets/splash.png)
