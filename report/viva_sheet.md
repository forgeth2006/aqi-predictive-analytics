---
title: "Viva sheet: Delhi AQI predictive analytics"
subtitle: "One line per technique: what it does, and what it showed in this project"
---

# The project in five sentences

1. Delhi, 1,826 days (2015-2019), nine pollutants and AQI from the Kaggle CPCB file; 2020 held out as a lockdown test.
2. PM2.5 and PM10 drive AQI (r = 0.88; β 0.43 and 0.38); 68% of days are Poor or worse.
3. Polynomial regression predicts AQI with R² 0.885; logistic regression predicts Poor days with AUC 0.981.
4. A trend + month regression forecasts monthly AQI 6 months ahead with 11.8% MAPE, 27% better than "same month last year".
5. Control charts flag the 2016 smog, the post-2017 improvement and the 2020 lockdown (4-7σ below the limits).

**The caveat to say first:** AQI is computed from the pollutants, so the same-day models partly recover the formula;
forecasting is the genuinely predictive part.

# Data wrangling

| Technique | What it does | What it showed |
| --- | --- | --- |
| Schema and duplicate check | confirms columns, removes repeated rows | 16 expected columns, 0 duplicates, complete daily calendar |
| Hidden-missing check | finds impossible values coded as numbers | CO = 0 for 84 days (Jun-Aug 2017): sensor outage, recoded as missing |
| Masked-value experiment | hides known values and scores imputation methods | interpolation best for short gaps (nRMSE 0.48), MICE for long gaps (1.08) |
| Linear interpolation | straight line between neighbouring days | best for 1-7 day gaps because AQI is persistent |
| MICE (iterative imputation) | predicts a missing pollutant from the others + season | best for long PM2.5/PM10/NO2 gaps |
| IQR rule | flags points beyond Q1 - 1.5 IQR / Q3 + 1.5 IQR | flags 3-10% of values, mostly genuine winter smog |
| Hampel filter | flags spikes vs a rolling median | isolated spikes flagged, kept |
| Winsorisation | caps extreme values at percentiles | 0.5/99.5 percentile caps, about 20 values per pollutant; AQI untouched |
| Data contract | automated checks on the cleaned file | 20/20 checks pass |

# Exploratory analysis

| Technique | What it does | What it showed |
| --- | --- | --- |
| Frequency table / bar / pie | counts days per AQI band | 1.3% Good, 12.9% Severe; winter has no Good day |
| Mean, median, mode | central tendency | AQI mean 266.3 ≈ median 266.0; PM2.5 mean 120 > median 98 |
| SD, variance, CV | spread | PM2.5 CV 68%; AQI SD 120 |
| Skewness | asymmetry (3rd moment) | PM2.5 1.39 (right-skewed); AQI only 0.26 |
| Kurtosis (excess) | tail weight (4th moment) | PM2.5 2.12 heavy-tailed; AQI -0.35 slightly flat |
| Normality tests (D'Agostino, JB) | test for a normal distribution | all reject; check residuals, not raw variables |
| Kruskal-Wallis / ANOVA | compare seasons | H = 930, ε² = 0.51: season explains half the variation |
| Pearson / Spearman correlation | linear / rank association | PM2.5 0.88/0.92; CO 0.27/0.54 (monotonic, non-linear) |
| Fisher z interval | CI for a correlation | PM2.5 r 0.874-0.894 |
| t confidence interval | CI for a mean | 260.8-271.8, too narrow because days are dependent |
| Effective sample size | n(1-ρ)/(1+ρ) for autocorrelated data | 1,826 days ≈ 98 independent; CI 242-290 |
| Wilson / block bootstrap CI | CI for a proportion | Poor share 68.0%; honest CI 59-76% |

# Regression

| Technique | What it does | What it showed |
| --- | --- | --- |
| Simple linear regression | AQI = β0 + β1·PM2.5 | AQI = 109.3 + 1.30·PM2.5, R² 0.783 |
| t and F tests | significance of slope / model | t = 72.6, F = 5,269 = t²; p < 0.001 |
| Confidence vs prediction interval | uncertainty of mean vs single day | at PM2.5 = 100: CI 237-243, PI 130-349 |
| Residual analysis | checks model assumptions | near-normal; DW 0.69 shows strong autocorrelation |
| Multiple regression | many predictors at once | R² 0.881; PM2.5 and PM10 dominate |
| Standardised (beta) coefficients | compares predictors in SD units | PM2.5 0.43, PM10 0.38, CO 0.13 |
| Dummy variables | categorical predictor (season) | monsoon 32.6 points below winter at equal pollution |
| VIF | multicollinearity | all < 6 (moderate) |
| Breusch-Pagan | heteroscedasticity | p ≈ 1e-15: variance grows with AQI |
| HC3 robust SE | inference despite heteroscedasticity | no verdict changed |
| Durbin-Watson | autocorrelation of errors | 1.10 in date order: positive autocorrelation |
| Cook's distance / leverage | influential points | max 0.05 (< 1); found an impossible PM2.5 > PM10 day |
| Log transformation | stabilise variance | made things worse (RMSE 70 vs 41), rejected |
| Backward elimination by AIC | model building | dropped SO2, NO2, NO |
| Polynomial term | curvature | PM2.5² significant; effect falls from 1.22 to 0.47 per µg/m³ |
| Partial F-test | tests a group of terms | season jointly significant (F = 18.6) |
| 10-fold CV / 2019 hold-out | honest generalisation | polynomial best: CV RMSE 40.2; 2019 R² 0.905 |

# Logistic and multinomial regression

| Technique | What it does | What it showed |
| --- | --- | --- |
| Logistic function | maps a score to a probability, 1/(1+e^-η) | median monsoon day P(Poor) = 0.025 |
| Likelihood-ratio test / pseudo R² | overall fit | p < 0.001; McFadden 0.741 |
| Wald test | significance of each coefficient, (β/SE)² | PM2.5, PM10, NOx, CO, O3, NO2 significant |
| Odds ratio | e^β, multiplicative change in odds | +10 µg/m³ PM2.5 → odds × 1.69 |
| Classification table | confusion matrix at a threshold | 11 missed Poor days, 11 false alarms, accuracy 0.940 |
| ROC curve / AUC | ranking quality across thresholds | AUC 0.981 |
| Gini coefficient | 2·AUC - 1 | 0.961 |
| Hosmer-Lemeshow | calibration goodness of fit | p = 0.73 (train), 0.60 (test): good fit |
| Cost-based threshold | trades misses vs false alarms | 3:1 cost → threshold 0.35, misses 11 → 7 |
| Quasi-separation | perfect prediction breaks MLE | why season is left out of the multinomial model |
| Multinomial logit | K-1 logit equations vs a baseline | accuracy 0.902, macro F1 0.854, AUC 0.973 |
| Relative risk ratio | e^β in the multinomial model | PM2.5 decisive; PM10 matters only for High vs Low |

# Decision trees

| Technique | What it does | What it showed |
| --- | --- | --- |
| CART classification tree | binary splits minimising Gini impurity | root split PM2.5 ≤ 76.3 (near the official 90 breakpoint) |
| Cross-validated tuning | chooses depth and leaf size | depth 8, ≥ 20 days per leaf |
| Cost-complexity pruning | removes weak branches (α) | 23 → 20 leaves, same accuracy |
| Feature importance | total impurity reduction | PM2.5 0.76, PM10 0.10 |
| CART regression tree | splits minimising squared error | R² 0.886, RMSE 40.3, lowest MAE |
| CHAID idea (chi-square) | splits on the most significant χ² | season vs AQI group χ² 779.6, Cramér's V 0.46 |
| Random forest (benchmark) | many averaged trees | AUC 0.982, no better than logistic |
| Unstructured data | text and images turned into features | fire counts and festival dates are the natural extension |

# Forecasting and time series

| Technique | What it does | What it showed |
| --- | --- | --- |
| STL / classical decomposition | trend + seasonal + remainder | seasonal strength 0.85; Nov +143, Jul -139 |
| ADF / KPSS | unit-root / stationarity tests | level non-stationary; differenced series stationary |
| ACF / PACF | identify AR and MA orders | AR(1) plus seasonal MA(1) at lag 12 |
| Moving average forecast | mean of the last k values | MA(3) fails on a seasonal series (MAPE 62%) |
| Simple exponential smoothing | geometrically weighted average | α = 0.995 → same as naive; fails |
| Holt-Winters | level + trend + seasonal smoothing | 2nd best, 18% skill |
| ARIMA(p,d,q) | Box-Jenkins without seasonality | (2,1,2): MAPE 46%, poor |
| SARIMA | adds seasonal terms | (1,0,0)(0,1,1)₁₂; seasonal MA ≈ -1 → deterministic seasonality |
| Ljung-Box | residual autocorrelation | SARIMA residuals white (p = 0.61) |
| Causal regression forecast | trend + month dummies (+ lagged pollutants) | **best**: rolling MAPE 11.8%, trend -19 AQI per year |
| GLS with AR(1) errors | corrects autocorrelated errors | ρ = 0.43; honest SEs, no accuracy gain |
| VAR | each series on lags of all series | VAR(3); NO2 and PM10 Granger-cause AQI |
| Granger causality | does X's past help predict Y? | NO2 → AQI p = 0.001; PM2.5 → AQI no (already in AQI's past) |
| Impulse response / FEVD | shock propagation / variance shares | PM10 explains 34% of AQI 6-month forecast variance |
| RMSE / MAPE | forecast accuracy | test RMSE 29.0, MAPE 13.9% |
| Rolling-origin evaluation | time-series cross-validation | 19 origins; robust model ranking |
| Prediction interval | range for future values | 95% PI ±85; Jan-Feb 2020 inside |
| Counterfactual forecast | what would have happened | Apr-Jun 2020 actual 36% below forecast = lockdown effect |
| ARMA errors, daily | next-day forecast | RMSE 50.2 vs persistence 54.0 |

# Control charts

| Technique | What it does | What it showed |
| --- | --- | --- |
| I-MR chart | individuals with σ = MR̄/1.128 | raw: mostly flags the season (14/60) |
| Seasonal adjustment | removes calendar effect | real signals: Oct-Nov 2016 smog, downward shift after 2017 |
| Western Electric rules | 1 beyond 3σ; 2/3 beyond 2σ; 4/5 beyond 1σ; 8 on one side | runs reveal a level shift |
| X̄-S chart | subgroup means and SDs | 45/60 outside: months are not rational subgroups |
| p-chart | proportion defective, variable n | 36/60 outside: over-dispersion (χ² 1,015 on 59 df) |
| Laney p′ chart | widens p limits by σz | σz 1.97; monsoon months remain low signals |
| Phase II monitoring | apply fixed limits to new data | Mar-Jun 2020 4.3-6.8σ below LCL: COVID-19 lockdown |

# Likely viva questions

* **Why not delete outliers?** They are real smog days, the very events studied; only sensor extremes were capped.
* **Why is the t-interval wrong?** Daily AQI is autocorrelated (r = 0.90), so the effective sample size is about 98.
* **Why does NH3 have a negative coefficient?** AQI is a *maximum* of sub-indices and NH3 correlates with PM2.5;
  it is not causal.
* **Why did the simplest forecasting model win?** The seasonality is deterministic (seasonal MA ≈ -1), so fixed month
  effects plus a trend capture it with the fewest parameters; SARIMA and VAR spend parameters on noise.
* **Why keep 2020 out?** The lockdown is a structural break; it is used as a natural experiment instead.
* **What would you add next?** Weather (wind, inversion height, rain) and satellite fire counts for the Oct-Nov peak.
