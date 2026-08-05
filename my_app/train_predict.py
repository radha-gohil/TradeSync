import numpy as np
import pandas as pd
import yfinance as yf
from tensorflow.keras.models import load_model
from .preprocessing import preprocess
from .models import CNN_LSTM
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

def train_and_predict(symbol):
    # Fetch last 1 year of data
    stock = yf.Ticker(symbol)
    data = stock.history(period="1y", interval="1d")

    # Ensure data is valid
    if data.empty:
        return {"error": "Invalid stock symbol or no data available"}

    # Reset index to make Date a column
    data.reset_index(inplace=True)
    
    # Preprocess data
    X, y, scaler = preprocess(data)

    # Build model
    model = CNN_LSTM((X.shape[1], 1))

    # Train model
    model.fit(X, y, epochs=50, batch_size=16, verbose=1)

    # Predictions
    y_pred = model.predict(X)
    y_pred_original = scaler.inverse_transform(y_pred)
    y_original = scaler.inverse_transform(y.reshape(-1, 1))

    # Calculate Accuracy Metrics
    r2 = r2_score(y_original, y_pred_original)
    mae = mean_absolute_error(y_original, y_pred_original)
    rmse = mean_squared_error(y_original, y_pred_original, squared=False)

    # Predict next 30 days
    last_60_days = X[-1]
    predictions = []
    for _ in range(30):
        next_day_pred = model.predict(last_60_days.reshape(1, -1, 1))
        predictions.append(next_day_pred[0, 0])
        last_60_days = np.roll(last_60_days, -1)
        last_60_days[-1] = next_day_pred

    predicted_prices = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
    
    return {
        "predictions": predicted_prices.tolist(),
        "r2_score": round(r2, 4),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "actual_prices": y_original.flatten().tolist(),
        "predicted_train": y_pred_original.flatten().tolist(),
        "dates_train": data["Date"][-len(y):].dt.strftime("%Y-%m-%d").tolist(),
        "forecast_dates": pd.date_range(start=data["Date"].iloc[-1] + pd.Timedelta(days=1), periods=30).strftime("%Y-%m-%d").tolist()
    }
