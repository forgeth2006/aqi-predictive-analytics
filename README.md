# Predicting and Forecasting Air Quality (AQI) Using Statistical and Predictive Models

Course project for **23XWA8 Predictive Analytics**. Daily air quality for **Delhi, 2015-01-01 to 2019-12-31**
(1,826 days), taken from raw data through cleaning, exploration, regression, classification, decision trees,
forecasting, time-series models and control charts to a deployed Streamlit app.

*Academic prototype. Not a health advisory and not an official forecast.*

**Live app:** _add the Streamlit Community Cloud link after deployment (see "Deploy" below)_

## Questions and answers

| Question | Answer |
| --- | --- |
| Which pollutants drive AQI, and how strongly? | **PM2.5 and PM10** (r = 0.88 each; standardised β 0.43 and 0.38). PM2.5 alone explains 78% of daily AQI variation. CO is third (β 0.13). |
| Can we predict a day's AQI and whether it is Poor or worse (AQI > 200)? | Yes. Polynomial regression: test R² 0.885, RMSE 40.5. Logistic regression: accuracy 0.940, ROC-AUC 0.981, Gini 0.961. Both hold up on a forward-in-time 2019 test. |
| Can we forecast monthly AQI 6 months ahead? | Yes. A trend + month regression has a rolling-origin MAPE of 11.8%, 27% better than "same month last year", and beats SARIMA, Holt-Winters and VAR. AQI is falling about 19 points a year. |
| When does the process go out of statistical control? | The Nov 2016 "Great Smog", a sustained improvement from mid-2017, and **March-June 2020**, when the COVID-19 lockdown pushed AQI 4-7 σ below the control limits (36% below the forecast). |

## Pipeline

| # | Notebook | Syllabus unit(s) | Main outputs |
| --- | --- | --- | --- |
| 01 | `01_wrangling.ipynb` | Data wrangling | `data/processed/aqi_delhi_clean.csv`, 2020 hold-out; imputation method chosen by a masked-value experiment |
| 02 | `02_eda.ipynb` | Data wrangling (EDA); tutorials 1-4 | frequency tables, moments, skewness/kurtosis, correlation, autocorrelation-aware confidence intervals |
| 03 | `03_regression.ipynb` | Linear regression; Multiple linear regression | simple, multiple (AIC backward elimination) and polynomial models, full diagnostics, `models/regression_model.json` |
| 04 | `04_classification.ipynb` | Logistic & multinomial regression; Decision trees | logit (Wald, Hosmer-Lemeshow, Gini, threshold tuning), multinomial, pruned CART classification and regression trees, CHAID chi-square, `models/classifier_models.json` |
| 05 | `05_timeseries.ipynb` | Forecasting; Time series analysis; tutorial 5 | MA, SES, Holt-Winters, ARIMA, SARIMA, causal regression, VAR (Granger, IRF, FEVD), rolling-origin evaluation, 2020 forecast vs COVID-19, daily ARMA next-day model |
| 06 | `06_control_charts.ipynb` | Tutorial 5 (SQC) | I-MR (raw and seasonally adjusted), X̄-S, p and Laney p′ charts, Phase II 2020 monitoring |

Every notebook is saved **with its outputs**, so it can be read without re-running.

## Syllabus coverage

| Unit (marks) | Where | What is done |
| --- | --- | --- |
| Data wrangling (5) | 01, 02 | ingest and schema check; duplicates; hidden missing values (CO = 0 outage); imputation chosen by experiment; IQR and Hampel outlier detection; winsorisation; univariate, bivariate and multivariate EDA |
| Linear regression (5) | 03 A | R², t and F tests, residual analysis, confidence vs prediction intervals |
| Multiple linear regression (10) | 03 B-D | coefficients and standardised betas, season as categorical, Breusch-Pagan, HC3 robust SEs, VIF, Cook's distance and leverage, Durbin-Watson, log transformation, backward elimination by AIC, polynomial term, partial F-tests, 10-fold CV, time-based test, imputation sensitivity |
| Logistic & multinomial regression (5) | 04 A-B | logistic function, probability estimation, LR test, Wald tests, odds ratios, Hosmer-Lemeshow, classification table, ROC, Gini, calibration, cost-based threshold; multinomial with RRRs |
| Decision trees (5) | 04 C | CART classification (tuned + cost-complexity pruned) and regression trees, Gini impurity, feature importance, CHAID chi-square test with Cramér's V, note on unstructured data |
| Forecasting (7) | 05 C-F | moving averages, simple and Holt-Winters exponential smoothing, causal regression forecast, RMSE/MAPE, rolling-origin evaluation, prediction intervals |
| Time series analysis (8) | 05 A-C, G | decomposition, ADF/KPSS, ACF/PACF, ARMA, ARIMA, SARIMA, VAR with Granger causality, IRF and FEVD, daily ARMA errors model |

Tutorial items: 1 classification and tabulation (02); 2 central tendency, dispersion, moments (02); 3 point and interval
estimates (02, 03); 4 correlation and regression (02, 03); 5 time series, forecasting and control charts (05, 06).

## Repository structure

```
data/raw/city_day.csv              Kaggle file (git-ignored; included in the project zip)
data/processed/                    aqi_delhi_clean.csv (2015-2019), aqi_delhi_2020_holdout.csv
notebooks/                         01_wrangling ... 06_control_charts (executed)
src/utils.py                       paths, constants, AQI band rules, metrics, plot style, JSON export
src/check_contract.py              data-contract checker for the cleaned file
src/predict_utils.py               predictions from the exported JSON models (numpy only)
models/                            regression_model.json, classifier_models.json
outputs/tables, outputs/figures    every result table (CSV) and figure (PNG)
outputs/forecast_monthly.csv       forecast for the app
outputs/control_chart.csv, p_chart.csv   control chart data for the app
app/app.py, app/tabs/              Streamlit app (Overview, EDA, Predict, Forecast, Control charts, Model performance)
report/                            project report (Markdown and Word) and viva sheet
tests/                             30 pytest checks (rules, data contract, outputs, app predictions)
scripts/run_all.py                 re-run every notebook in order, then the contract check and tests
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate             # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -r requirements-notebooks.txt
```

`requirements.txt` holds only what the deployed app needs; `requirements-notebooks.txt` adds statsmodels, scikit-learn,
seaborn, Jupyter and pytest. statsmodels must be **0.14.5 or newer** (older versions fail to import with SciPy ≥ 1.16).

## Run

```bash
streamlit run app/app.py           # the app (reads the saved outputs; trains nothing)
python src/check_contract.py       # verify the cleaned data
python -m pytest -q tests          # 30 tests
python scripts/run_all.py          # optional: re-execute all six notebooks from the raw file (about 5 minutes)
```

## Deploy (Streamlit Community Cloud)

1. Push the repository to GitHub (the raw Kaggle CSV is git-ignored; the app does not need it).
2. On share.streamlit.io choose **New app**, pick the repo and branch, and set the main file to `app/app.py`.
3. The platform installs `requirements.txt` automatically. Paste the app link at the top of this README.

## Data

Kaggle, *Air Quality Data in India (2015 - 2020)* by Vopani, file `city_day.csv` (CPCB data; 29,531 rows, 26 cities).
Columns: City, Date, PM2.5, PM10, NO, NO2, NOx, NH3, CO, SO2, O3, Benzene, Toluene, Xylene, AQI, AQI_Bucket.
Benzene, Toluene and Xylene are dropped (not part of the Indian AQI). Units: µg/m³, CO in mg/m³. Check the dataset
licence on Kaggle before redistributing the raw file.

## Limitations

* AQI is computed from the pollutant readings, so the regression and classification models partly recover the AQI
  formula; they quantify drivers rather than discover new science. Forecasting (notebook 05) is the genuinely predictive part.
* One city and five years; 2020 is a structural break and is used only as a hold-out.
* Long sensor outages (58-84 days) cannot be imputed precisely by any method; every imputed value is flagged in the
  `Imputed` column and a sensitivity check shows the main regression conclusions do not depend on them.
* No weather data (wind, temperature, boundary-layer height) or fire counts, the obvious next step for sharper forecasts.
