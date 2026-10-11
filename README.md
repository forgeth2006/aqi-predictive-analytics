# Predicting and Forecasting Air Quality (AQI) Using Statistical and Predictive Models

Course project for 23XWA8 Predictive Analytics. Daily Delhi AQI, 2015-01-01 to 2019-12-31.
Academic prototype. Not a health advisory and not an official forecast.

**Live app:** _add the Streamlit link after deployment_

## Team
- Member 1 (Hephzi): regression, logistic and multinomial regression, CART, model comparison, saved models, deployment
- Member 2: data wrangling, EDA, forecasting and time series, control charts

## Data
Kaggle "Air Quality Data in India (2015 - 2020)", file `city_day.csv`.
Download it and place it at `data/raw/city_day.csv` (it is git-ignored).
The cleaned file `data/processed/aqi_delhi_clean.csv` follows the data contract in the project pack.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## First cell of every notebook
```python
import sys
from pathlib import Path
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT))
from src.utils import *          # paths, SEED, metrics, plot style
set_plot_style()
```

## Run
```bash
python src/check_contract.py     # Gate M1 test for the cleaned data
streamlit run app/app.py         # the app
```

## Structure
```
data/raw, data/processed         datasets
notebooks/                       01_wrangling, 02_eda, 03_regression, 04_classification,
                                 05_timeseries, 06_control_charts
src/utils.py                     paths, constants, metrics, plot style (Member 1)
src/check_contract.py            data contract checker (Member 1)
models/                          saved models (*.joblib)
outputs/tables, outputs/figures  results
app/app.py, app/tabs/            Streamlit app
report/                          report sections
```

## Status
| Gate | State |
| --- | --- |
| M0 Kickoff | |
| M1 Clean data | |
| M2 Analysis notebooks | |
| M3 Integration | |
| M4 Release | |
