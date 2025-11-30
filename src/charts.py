import plotly.express as px
import pandas as pd

def plot_correlation(df):
    df = df.select_dtypes(include=["int64","float64"])
    df = df.loc[:, ~df.columns.duplicated()].copy()

    corr = df.corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="Viridis",
        title="Correlation Heatmap"
    )
    return fig
