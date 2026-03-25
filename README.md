# Premier League Analytics Dashboard

An interactive visualization dashboard for exploring Premier League team performance across multiple seasons.

## Features

- **Line Chart**: Historical goals scored by team across seasons
- **Scatter Plot**: Goals conceded vs. goals scored (bubble size = points earned)
- **Bar Chart**: Points and placement by season across teams
- **Unified Filtering**: Single control panel filters all visualizations simultaneously
- **Interactive Interactions**: Click on charts to toggle team selection, hover for detailed metrics

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
python app.py
```

The dashboard will open at `http://127.0.0.1:8050/`

## Project Structure

```
dashboard/
├── app.py                      # Main Dash application
├── team_colors.py              # Color mapping for teams
├── team_stats_by_season.csv    # Data file
├── assets/
│   └── style.css              # Dashboard styling
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```