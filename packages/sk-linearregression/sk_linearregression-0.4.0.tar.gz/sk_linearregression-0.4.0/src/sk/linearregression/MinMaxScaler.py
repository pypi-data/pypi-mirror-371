import numpy as np
import pandas as pd

class MinMaxScaler:
    def __init__(self, feature_range=(0,1)):
        self.min_range, self.max_range = feature_range
        self.data_min_ = None
        self.data_max_ = None

    def fit(self, X):
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        self.numeric_cols = numeric_cols
        self.data_min_ = X[numeric_cols].min()
        self.data_max_ = X[numeric_cols].max()
        return self

    def transform(self, X):
        X = X.copy()
        denom = (self.data_max_ - self.data_min_)
        denom[denom == 0] = 1  # avoid division by zero

        X_scaled = (X[self.numeric_cols] - self.data_min_) / denom
        X_scaled = X_scaled * (self.max_range - self.min_range) + self.min_range

        X[self.numeric_cols] = X_scaled
        return X

    def fit_transform(self, X):
        return self.fit(X).transform(X)
