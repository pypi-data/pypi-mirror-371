# sk.linearregression

🚀 My first Python package on PyPI!  

This package provides a simple implementation of **Linear Regression** along with helpful preprocessing utilities such as handling missing values, scaling data, and splitting into train/test sets.

---

## ✨ Features
- `LinearRegression` – Simple regression model
- `HandleMissingValue` – Fill or drop missing values
- `MinMaxScaler` – Normalize features to a given range
- `TrainTestSplit` – Split your dataset into training and testing sets

---

## 📦 Installation
Install directly from PyPI:
```bash
pip install sk.linearregression




# Sample Uses
from sk.linearregression import LinearRegression, HandleMissingValue, TrainTestSplit, MinMaxScaler
import pandas as pd
import matplotlib.pyplot as plt

def main():
    df = pd.read_csv("train.csv")

    Y = df["SalePrice"]
    X = df.drop(columns=["SalePrice", "Id"])
    X = HandleMissingValue(X)

    X_train, X_test, Y_train, Y_test = TrainTestSplit(X, Y)

    X_train = MinMaxScaler(X_train)
    X_test = MinMaxScaler(X_test)
    
    obj = LinearRegression(X_train, Y_train)
    w, b = obj.regression()
    y_pred = obj.predict(X_test.values.astype(float), w, b)

    plt.figure(figsize=(10, 5))
    plt.plot(Y_test.values[:100], label='Actual', marker='o')  # Use .values if it's a Pandas Series
    plt.plot(y_pred[:100], label='Predicted', marker='x')
    plt.title("Comparison of Actual vs Predicted (First 100 Samples)")
    plt.xlabel("Sample Index")
    plt.ylabel("Target Value")
    plt.legend()
    plt.show()