import pandas as pd
import numpy as np

class SmartCleaner:
    """
    SmartCleaner: A lightweight toolkit for common data cleaning tasks.
    """

    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        self.df = df.copy()

    def remove_duplicates(self):
        """Remove duplicate rows"""
        before = len(self.df)
        self.df = self.df.drop_duplicates()
        after = len(self.df)
        return f"Removed {before - after} duplicates"

    def fill_missing(self, strategy="mean"):
        """Fill missing values with mean, median, mode, or zero"""
        for col in self.df.select_dtypes(include=[np.number]).columns:
            if strategy == "mean":
                self.df[col] = self.df[col].fillna(self.df[col].mean())
            elif strategy == "median":
                self.df[col] = self.df[col].fillna(self.df[col].median())
            elif strategy == "mode":
                self.df[col] = self.df[col].fillna(self.df[col].mode()[0])
            elif strategy == "zero":
                self.df[col] = self.df[col].fillna(0)
        return f"Filled missing values using {strategy}"

    def standardize_columns(self):
        """Make all column names lowercase and snake_case"""
        self.df.columns = (
            self.df.columns.str.strip().str.lower().str.replace(" ", "_")
        )
        return "Standardized column names"

    def remove_outliers(self, method="zscore", threshold=3):
        """Remove outliers using z-score or IQR"""
        if method == "zscore":
            from scipy.stats import zscore
            z_scores = np.abs(self.df.select_dtypes(include=[np.number]).apply(zscore))
            self.df = self.df[(z_scores < threshold).all(axis=1)]
        elif method == "iqr":
            Q1 = self.df.quantile(0.25)
            Q3 = self.df.quantile(0.75)
            IQR = Q3 - Q1
            self.df = self.df[~((self.df < (Q1 - 1.5 * IQR)) | (self.df > (Q3 + 1.5 * IQR))).any(axis=1)]
        return f"Removed outliers using {method}"

    def get_cleaned_data(self):
        return self.df
