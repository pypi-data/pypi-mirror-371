import pandas as pd
import pytest
from smartcleaner import SmartCleaner

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Name": ["Alice", "Bob", "Alice", None],
        "Age": [25, None, 25, 30],
        "Salary": [50000, 60000, 50000, None]
    })

def test_remove_duplicates(sample_df):
    sc = SmartCleaner(sample_df)
    msg = sc.remove_duplicates()
    assert "Removed" in msg
    assert len(sc.df) < len(sample_df)

def test_fill_missing_mean(sample_df):
    sc = SmartCleaner(sample_df)
    sc.fill_missing(strategy="mean")
    assert sc.df["Age"].isna().sum() == 0
    assert sc.df["Salary"].isna().sum() == 0

def test_standardize_columns(sample_df):
    sc = SmartCleaner(sample_df)
    sc.standardize_columns()
    assert all(col.islower() for col in sc.df.columns)

def test_remove_outliers_zscore(sample_df):
    sc = SmartCleaner(sample_df)
    sc.fill_missing("mean")
    sc.remove_outliers("zscore")
    assert isinstance(sc.df, pd.DataFrame)

def test_get_cleaned_data(sample_df):
    sc = SmartCleaner(sample_df)
    cleaned = sc.get_cleaned_data()
    assert isinstance(cleaned, pd.DataFrame)
