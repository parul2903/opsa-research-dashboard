import pandas as pd

def basic_info(df):
    info = {
        "Rows": len(df),
        "Columns": len(df.columns),
        "Missing Values": df.isnull().sum().sum(),
        "Numeric Columns": df.select_dtypes(include=["int64","float64"]).columns.tolist(),
        "Categorical Columns": df.select_dtypes(include=["object"]).columns.tolist(),
    }
    return info

def summary_statistics(df):
    return df.describe(include="all").transpose()
