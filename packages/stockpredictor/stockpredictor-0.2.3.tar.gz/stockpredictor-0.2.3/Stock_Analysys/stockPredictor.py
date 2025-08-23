import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from mpl_toolkits.mplot3d import Axes3D
import os

class StockPredictor:
    def __init__(self, ticker="^NSEI", start="2020-01-01", end="2024-01-01", save_dir="outputs"):
        self.ticker = ticker
        self.start = start
        self.end = end
        self.data = None
        self.model = None
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def load_data(self, save=False):
        """Download index data from Yahoo Finance"""
        self.data = yf.download(self.ticker, start=self.start, end=self.end)
        self.data.dropna(inplace=True)
        print(f"Data loaded: {self.data.shape[0]} rows")

        if save:
            path = os.path.join(self.save_dir, "data_raw.csv")
            self.data.to_csv(path)
            print(f"Saved raw data to {path}")
        return self.data

    def prepare_features(self, save=False):
        """Create features & target for prediction"""
        df = self.data.copy()

        # Moving averages
        df["MA5"] = df["Close"].rolling(window=5).mean()
        df["MA20"] = df["Close"].rolling(window=20).mean()
        df["MA50"] = df["Close"].rolling(window=50).mean()

        # Returns
        df["Returns"] = df["Close"].pct_change()

        # RSI (Relative Strength Index)
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # MACD
        ema12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema26 = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = ema12 - ema26
        df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

        # Bollinger Bands
        rolling_mean = df["Close"].rolling(window=20).mean()
        rolling_std = df["Close"].rolling(window=20).std()
        df["Bollinger_Upper"] = rolling_mean + (rolling_std * 2)
        df["Bollinger_Lower"] =\
            rolling_mean - (rolling_std * 2)

        df.dropna(inplace=True)

        # Features
        self.X = df[["Open", "High", "Low", "Close", "Volume",
                     "MA5", "MA20", "MA50", "Returns", "RSI", "MACD", "Signal",
                     "Bollinger_Upper", "Bollinger_Lower"]]

        # Target: 1 if price goes up tomorrow, else 0
        df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
        self.y = df["Target"]
        self.data = df

        if save:
            path = os.path.join(self.save_dir, "data_features.csv")
            df.to_csv(path)
            print(f"Saved features to {path}")

    def train_linear(self):
        reg = LinearRegression()
        reg.fit(self.X, self.y)
        self.model = reg
        print("Linear regression trained")
        return reg.coef_, reg.intercept_

    def train_logistic(self):
        log_reg = LogisticRegression(max_iter=2000)
        log_reg.fit(self.X, self.y)
        self.model = log_reg
        print("Logistic regression trained")
        return log_reg.score(self.X, self.y)

    def predict(self, save=False):
        if self.model is None:
            raise ValueError("Model not trained")
        preds = self.model.predict(self.X)
        self.data["Predictions"] = preds

        if save:
            path = os.path.join(self.save_dir, "predictions.csv")
            self.data[["Close", "Target", "Predictions"]].to_csv(path)
            print(f"Saved predictions to {path}")
        return preds

    def evaluate(self, save=False):
        preds = self.predict()
        acc = accuracy_score(self.y, preds)
        cm = confusion_matrix(self.y, preds)
        report = classification_report(self.y, preds, output_dict=True)

        print(f"Accuracy: {acc:.2%}")
        print(cm)
        print(classification_report(self.y, preds))

        if save:
            path = os.path.join(self.save_dir, "evaluation.csv")
            df_report = pd.DataFrame(report).transpose()
            df_report.to_csv(path)
            print(f"Saved evaluation report to {path}")

        return acc, cm, report

    def plot(self):
        plt.figure(figsize=(12,6))
        plt.plot(self.data["Close"], label="Close Price")
        plt.plot(self.data["MA20"], label="MA20")
        plt.plot(self.data["Bollinger_Upper"], label="Bollinger Upper")
        plt.plot(self.data["Bollinger_Lower"], label="Bollinger Lower")
        plt.legend()
        plt.title(f"{self.ticker} Price & Indicators")
        plt.show()

    def plot_3d(self, feature_x="RSI", feature_y="MACD"):
        if feature_x not in self.X.columns or feature_y not in self.X.columns:
            raise ValueError("Invalid feature for 3D plot")
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(self.X[feature_x], self.X[feature_y], self.data["Target"], c=self.data["Target"], cmap="coolwarm")
        ax.set_xlabel(feature_x)
        ax.set_ylabel(feature_y)
        ax.set_zlabel("Target")
        plt.title(f"3D Plot: {feature_x} vs {feature_y} vs Target")
        plt.show()
