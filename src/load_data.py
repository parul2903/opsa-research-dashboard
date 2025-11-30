import pandas as pd
import os

def load_dataset(path):
    """
    Safely load dataset and fix all duplicate column issues.
    Compatible with Pandas 1.x and 2.x.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)

    # Strip whitespace
    df.columns = df.columns.str.strip()

    # Remove duplicate columns (keep first)
    df = df.loc[:, ~df.columns.duplicated()].copy()

    # Rename duplicates for safety: col, col_1, col_2, ...
    cols = df.columns.tolist()
    new_cols, seen = [], {}

    for c in cols:
        if c not in seen:
            seen[c] = 0
            new_cols.append(c)
        else:
            seen[c] += 1
            new_cols.append(f"{c}_{seen[c]}")

    df.columns = new_cols

    # Final duplicate cleanup
    df = df.loc[:, ~df.columns.duplicated()].copy()

    return df
