# DATFID SDK

A Python SDK to access the DATFID API running on Hugging Face Spaces.

## Installation

```bash
pip install datfid
```

## Usage

```python
from datfid import DATFIDClient

# Initialize the client with your Hugging Face token
client = DATFIDClient(token="your_huggingface_token")

# Fit a model
fit_result = client.fit_model(
    file_path="path/to/your/data.xlsx",
    id_col="Individual",
    time_col="Time",
    y="Loan Probability",
    lagged_features={"Repayment Amount": 1, "Missed Payments": 2},
    current_features=["Credit Score", "Unemployment Rate"],
    filter_by_significance=True,
    meanvar_test=False
)

# Generate forecasts
forecast_df = client.generate_forecast(
    file_path="path/to/your/forecast_data.xlsx",
    id_col="Individual",
    time_col="Time",
    y="Loan Probability",
    lagged_features={"Repayment Amount": 1, "Missed Payments": 2},
    current_features=["Credit Score", "Unemployment Rate"],
    filter_by_significance=True,
    meanvar_test=False
)

# The forecast DataFrame includes the original data plus forecast columns:
# - forecast: The predicted values
# - forecast_lower: Lower bound of the prediction interval
# - forecast_upper: Upper bound of the prediction interval
# - forecast_error: Standard error of the forecast
```

## API Reference

### DATFIDClient

#### `__init__(token: str)`
Initialize the client with your Hugging Face token.

#### `fit_model(file_path: str, id_col: str, time_col: str, y: str, lagged_features: Optional[Dict[str, int]] = None, current_features: Optional[list] = None, filter_by_significance: bool = False, meanvar_test: bool = False) -> Dict[str, Any]`
Fit a model using the provided data.

#### `generate_forecast(file_path: str, id_col: str, time_col: str, y: str, lagged_features: Optional[Dict[str, int]] = None, current_features: Optional[list] = None, filter_by_significance: bool = False, meanvar_test: bool = False) -> pd.DataFrame`
Generate forecasts using the fitted model.
