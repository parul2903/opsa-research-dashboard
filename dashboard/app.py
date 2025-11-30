# ======================================================================
#                 GLOBAL RESEARCH ANALYTICS DASHBOARD
#                 POWER BI PREMIUM DARK — FINAL VERSION
# ======================================================================

import os, sys, warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ------------------------------------------------------------
# FIX PATHS FOR src/ MODULES
# ------------------------------------------------------------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.load_data import load_dataset
from src.eda_functions import basic_info, summary_statistics
from src.charts import plot_correlation

# ======================================================================
#                       STREAMLIT PAGE CONFIG
# ======================================================================
st.set_page_config(
    page_title="Global Research Analytics Dashboard",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# ======================================================================
#                     POWER BI PREMIUM DARK THEME
# ======================================================================
POWERBI_DARK = """
<style>
body, .block-container {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
    font-family: 'Segoe UI', sans-serif;
}
.sidebar .sidebar-content {
    background-color: #161b22 !important;
}
h1, h2, h3, h4 {
    color: #4cb4ff !important;
    font-weight: 650 !important;
}
.metric-card {
    background-color: #11161f !important;
    border-radius: 12px;
    padding: 14px;
    box-shadow: 0 0 12px rgba(0,0,0,0.45);
}
</style>
"""

st.markdown(POWERBI_DARK, unsafe_allow_html=True)

# ======================================================================
#                   LOAD DATA + CLEAN DUPLICATE COLUMNS
# ======================================================================
DATA_PATH = os.path.join(ROOT, "data", "publications.csv")
df = load_dataset(DATA_PATH)

# Remove duplicate column names if any
df = df.loc[:, ~df.columns.duplicated()].copy()

num_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
cat_cols = df.select_dtypes(include=["object"]).columns.tolist()

# ======================================================================
#               ADVANCED SCIENTOMETRIC KPI CALCULATIONS
# ======================================================================

df["Citation Efficiency"] = df["Times Cited"] / df["Web of Science Documents"]

df["Excellence Rate (Top 1%)"] = (
    df["Documents in Top 1%"] / df["Web of Science Documents"]
)

df["High Impact Rate (Top 10%)"] = (
    df["Documents in Top 10%"] / df["Web of Science Documents"]
)

df["Citation Quality Index"] = (
    df["Category Normalized Citation Impact"] *
    (df["Times Cited"] / df["Web of Science Documents"])
)

df["Collaboration Advantage"] = (
    df["Collab-CNCI"] / df["Category Normalized Citation Impact"]
)

df["Rank Efficiency"] = (
    df["Web of Science Documents"] / df["Rank"]
)

total_citations = df["Times Cited"].sum()
df["Citation Dominance"] = df["Times Cited"] / total_citations

df["Quality Weighted Output"] = (
    df["Web of Science Documents"] * df["Category Normalized Citation Impact"]
)

df["Impact per Excellence"] = (
    df["Times Cited"] / df["Documents in Top 10%"]
)

current_year = df["year"].max()
df["Citation Velocity"] = (
    df["Times Cited"] / (current_year - df["year"] + 1)
)

# ======================================================================
#                       SIDEBAR NAVIGATION MENU
# ======================================================================
st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Go to Page",
    [
        "🏠 Executive Overview",
        "📊 Research Performance",
        "📐 Advanced KPI Analytics",
        "🎯 Country Drillthrough Dashboard"
    ]
)

# ======================================================================
#                         GLOBAL FILTERS (POWER BI STYLE)
# ======================================================================
st.sidebar.title("🎛 Global Filters")

# Text Search
search_term = st.sidebar.text_input("🔍 Search Country")

# Country Filter
country_filter = st.sidebar.multiselect(
    "🌍 Select Countries",
    sorted(df["Name"].unique()),
    default=sorted(df["Name"].unique())
)

# Year Multi-Select Filter (NEW)
if "year" in df.columns:
    year_filter = st.sidebar.multiselect(
        "📅 Select Years",
        sorted(df["year"].unique()),
        default=sorted(df["year"].unique())
    )
else:
    year_filter = None

# Numeric Filters
num_filters = {}
for col in num_cols:
    mn, mx = float(df[col].min()), float(df[col].max())
    num_filters[col] = st.sidebar.slider(
        f"{col}",
        mn, mx, (mn, mx)
    )

# ======================================================================
#                 APPLYING FILTERS TO DATA
# ======================================================================
filtered = df.copy()

if search_term:
    filtered = filtered[
        filtered["Name"].str.contains(search_term, case=False, na=False)
    ]

filtered = filtered[filtered["Name"].isin(country_filter)]

if year_filter:
    filtered = filtered[filtered["year"].isin(year_filter)]

for col in num_cols:
    lo, hi = num_filters[col]
    filtered = filtered[filtered[col].between(lo, hi)]

filtered = filtered.loc[:, ~filtered.columns.duplicated()]

st.sidebar.success(f"Filtered Rows: {len(filtered)}")

# ======================================================================
#                         PAGE 1 — EXECUTIVE OVERVIEW
# ======================================================================

if page == "🏠 Executive Overview":

    st.title("🏠 Executive Overview")
    st.markdown("""
A high-level, executive summary of global scientific performance across
productivity, influence, quality, collaboration strength, and excellence.
""")

    # ==================================================================
    #                           KPI CARDS (TOP ROW)
    # ==================================================================
    st.markdown("## 📌 Key Performance Indicators (Global Metrics)")

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Countries", len(filtered["Name"].unique()))
        st.markdown("</div>", unsafe_allow_html=True)

    with k2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric(
            "Total Documents",
            f"{filtered['Web of Science Documents'].sum():,}"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with k3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric(
            "Total Citations",
            f"{filtered['Times Cited'].sum():,}"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with k4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric(
            "Avg CNCI",
            round(filtered["Category Normalized Citation Impact"].mean(), 3)
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ==================================================================
    #                  HIGH-LEVEL CHARTS — PRODUCTIVITY & IMPACT
    # ==================================================================
    st.markdown("## 📊 Research Output & Scientific Influence")

    colA, colB = st.columns(2)

    # ----- Chart A: Documents by Country -----
    with colA:
        st.subheader("Total Documents by Country")

        docs = (
            filtered.groupby("Name")["Web of Science Documents"]
            .sum()
            .reset_index()
            .sort_values("Web of Science Documents", ascending=False)
        )

        figA = px.bar(
            docs,
            x="Name",
            y="Web of Science Documents",
            color="Web of Science Documents",
            color_continuous_scale="Blues",
            height=450,
            title="Research Output (Publications)"
        )
        figA.update_layout(showlegend=False)
        st.plotly_chart(figA, use_container_width=True)

    # ----- Chart B: Citations by Country -----
    with colB:
        st.subheader("Total Citations by Country")

        cites = (
            filtered.groupby("Name")["Times Cited"]
            .sum()
            .reset_index()
            .sort_values("Times Cited", ascending=False)
        )

        figB = px.bar(
            cites,
            x="Name",
            y="Times Cited",
            color="Times Cited",
            color_continuous_scale="Purples",
            height=450,
            title="Scientific Influence (Citations)"
        )
        figB.update_layout(showlegend=False)
        st.plotly_chart(figB, use_container_width=True)

    st.markdown("---")

    # ==================================================================
    #                       SUMMARY TABLE
    # ==================================================================
    st.markdown("## 📄 Summary Table (Core Metrics)")

    summary_table = filtered[[
        "Name",
        "Web of Science Documents",
        "Times Cited",
        "Category Normalized Citation Impact",
        "Rank",
        "Documents in Top 1%",
        "Documents in Top 10%",
        "Citation Efficiency",
        "High Impact Rate (Top 10%)"
    ]].sort_values("Times Cited", ascending=False)

    st.dataframe(summary_table, use_container_width=True)

    st.markdown("---")

    # ==================================================================
    #                         EXECUTIVE INSIGHTS
    # ==================================================================
    st.markdown("## 🔍 Key Executive Insights")

    top_docs = filtered.loc[filtered["Web of Science Documents"].idxmax()]
    top_cites = filtered.loc[filtered["Times Cited"].idxmax()]
    top_cnci = filtered.loc[filtered["Category Normalized Citation Impact"].idxmax()]
    top_top10 = filtered.loc[filtered["Documents in Top 10%"].idxmax()]

    st.markdown(f"""
### 🌍 Productivity Leaders
- **{top_docs['Name']}** produces the highest number of documents  
  (**{top_docs['Web of Science Documents']:,} papers**).

### ⭐ Global Influence (Citations)
- **{top_cites['Name']}** provides the largest citation impact globally  
  (**{top_cites['Times Cited']:,} citations**).

### 📈 Research Quality (CNCI)
- Best CNCI score belongs to **{top_cnci['Name']}** (CNCI = {top_cnci['Category Normalized Citation Impact']:.2f})  
  → Indicates above world-average research quality.

### 🏆 High Impact Excellence
- **{top_top10['Name']}** generates the highest number of high-impact Top 10% papers  
  (**{top_top10['Documents in Top 10%']}** papers).

---

### 📌 Overall Interpretation
- Countries with strong CNCI & Top 10% output are global research leaders.
- High publication volume does **not** guarantee high impact → quality matters more.
- Collaboration metrics strongly correlate with higher citation impact.
- Citation efficiency reveals which countries produce “more impact per paper.”
""")


# ======================================================================
#                    PAGE 2 — RESEARCH PERFORMANCE
# ======================================================================

elif page == "📊 Research Performance":

    st.title("📊 Research Performance Dashboard")
    st.markdown("""
This dashboard presents the core scientometric indicators across productivity,
impact, citation efficiency, research quality, and excellence.
""")

    # ==============================================================
    #                       TOP KPI BAR — CLEAN 5 METRICS
    # ==============================================================
    st.markdown("## 📌 Major Scientific Indicators")

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Total Documents", f"{filtered['Web of Science Documents'].sum():,}")
        st.markdown("</div>", unsafe_allow_html=True)

    with k2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Total Citations", f"{filtered['Times Cited'].sum():,}")
        st.markdown("</div>", unsafe_allow_html=True)

    with k3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Avg CNCI", round(filtered["Category Normalized Citation Impact"].mean(), 2))
        st.markdown("</div>", unsafe_allow_html=True)

    with k4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Citation Efficiency",
                  round(filtered["Citation Efficiency"].mean(), 2))
        st.markdown("</div>", unsafe_allow_html=True)

    with k5:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Avg High Impact Rate",
                  f"{round(filtered['High Impact Rate (Top 10%)'].mean()*100, 2)}%")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ==============================================================
    #               ROW 1 — DOCUMENTS & CITATIONS
    # ==============================================================

    st.markdown("## 📊 Research Output & Scientific Influence")

    c1, c2 = st.columns(2)

    # ---------------- Chart 1: Publication Volume ----------------
    with c1:
        st.subheader("Total Publications (Documents)")

        docs = (
            filtered.groupby("Name")["Web of Science Documents"]
            .sum().reset_index().sort_values("Web of Science Documents", ascending=False)
        )

        fig1 = px.bar(
            docs,
            x="Name",
            y="Web of Science Documents",
            color="Web of Science Documents",
            color_continuous_scale="Blues",
            title="Research Output by Country"
        )
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

    # ---------------- Chart 2: Total Citations ----------------
    with c2:
        st.subheader("Total Citations (Impact)")

        cites = (
            filtered.groupby("Name")["Times Cited"]
            .sum().reset_index().sort_values("Times Cited", ascending=False)
        )

        fig2 = px.bar(
            cites,
            x="Name",
            y="Times Cited",
            color="Times Cited",
            color_continuous_scale="Purples",
            title="Scientific Influence by Country"
        )
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # ---------------- Insights ----------------
    st.markdown("### 🔍 Insights")
    st.write("""
- Switzerland shows high productivity and very high impact.
- The UK produces fewer papers but extremely influential ones.
- China shows strong growth and rising impact.
""")

    st.markdown("---")

    # ==============================================================
    #            ROW 2 — EFFICIENCY & QUALITY
    # ==============================================================

    st.markdown("## ⚙️ Citation Efficiency & Research Quality")

    c3, c4 = st.columns(2)

    # ---------------- Efficiency Chart ----------------
    with c3:
        st.subheader("Citation Efficiency (Impact per Publication)")

        eff = filtered.sort_values("Citation Efficiency", ascending=False)

        fig3 = px.bar(
            eff,
            x="Name",
            y="Citation Efficiency",
            color="Citation Efficiency",
            color_continuous_scale="Viridis",
            title="Citations per Paper"
        )
        fig3.update_layout(showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    # ---------------- Quality Weighted Output Chart ----------------
    with c4:
        st.subheader("Quality Weighted Output (Docs × CNCI)")

        qwo = filtered.sort_values("Quality Weighted Output", ascending=False)

        fig4 = px.bar(
            qwo,
            x="Name",
            y="Quality Weighted Output",
            color="Quality Weighted Output",
            color_continuous_scale="Teal",
            title="Quality-Adjusted Impact"
        )
        fig4.update_layout(showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("### 🔍 Insights")
    st.write("""
- UK leads in pure citation efficiency → high quality.
- Switzerland and China (2013) show high quality-weighted output.
""")

    st.markdown("---")

    # ==============================================================
    #                      ROW 3 — EXCELLENCE
    # ==============================================================

    st.markdown("## 🏆 High-Impact Excellence Metrics")

    c5, c6 = st.columns(2)

    # Top 1%
    with c5:
        st.subheader("Elite Output — Top 1% Most Influential Papers")

        fig5 = px.bar(
            filtered.sort_values("Documents in Top 1%", ascending=False),
            x="Name",
            y="Documents in Top 1%",
            color="Documents in Top 1%",
            color_continuous_scale="Mint",
            title="Top 1% Papers"
        )
        fig5.update_layout(showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)

    # Top 10%
    with c6:
        st.subheader("High-Impact Output — Top 10% Papers")

        fig6 = px.bar(
            filtered.sort_values("Documents in Top 10%", ascending=False),
            x="Name",
            y="Documents in Top 10%",
            color="Documents in Top 10%",
            color_continuous_scale="Burgyl",
            title="Top 10% Papers"
        )
        fig6.update_layout(showlegend=False)
        st.plotly_chart(fig6, use_container_width=True)

    st.markdown("### 🔍 Insights")
    st.write("""
- UK produces very high proportions of high-impact work.
- China (2013) displays emerging excellence strength.
- Switzerland maintains globally influential work despite smaller size.
""")

    st.markdown("---")

    # ==============================================================
    #                 ROW 4 — COLLABORATION
    # ==============================================================

    st.markdown("## 🤝 Collaboration Metrics")

    col7, col8 = st.columns(2)

    with col7:
        st.subheader("Collaboration Advantage (Collab-CNCI / CNCI)")

        fig7 = px.bar(
            filtered.sort_values("Collaboration Advantage", ascending=False),
            x="Name",
            y="Collaboration Advantage",
            color="Collaboration Advantage",
            color_continuous_scale="Plasma",
            title="Impact Benefit from Collaboration"
        )
        fig7.update_layout(showlegend=False)
        st.plotly_chart(fig7, use_container_width=True)

    with col8:
        st.subheader("Citation Dominance Share (%)")

        dom = filtered.copy()
        dom["Citation Dominance %"] = dom["Citation Dominance"] * 100

        fig8 = px.pie(
            dom,
            names="Name",
            values="Citation Dominance %",
            title="Share of Global Citations",
            hole=0.4
        )
        st.plotly_chart(fig8, use_container_width=True)

    st.markdown("### 🔍 Insights")
    st.write("""
- Collaboration strongly boosts CNCI and total impact.
- Countries with higher global citation shares show stronger research ecosystems.
""")

# ======================================================================
#                   PAGE 3 — ADVANCED KPI ANALYTICS
# ======================================================================

elif page == "📐 Advanced KPI Analytics":

    st.title("📐 Advanced KPI Analytics")
    st.markdown("""
Explore deep scientometric indicators derived from productivity, impact,
quality, efficiency, excellence, and collaboration.
This section is designed for data scientists, policymakers, and analysts.
""")

    # ============================================================
    #               KPI SELECTION (Dropdown)
    # ============================================================

    st.markdown("## 🎛 Select KPI for Deep Analysis")

    kpi_options = [
        "Citation Efficiency",
        "Excellence Rate (Top 1%)",
        "High Impact Rate (Top 10%)",
        "Citation Quality Index",
        "Collaboration Advantage",
        "Rank Efficiency",
        "Citation Dominance",
        "Quality Weighted Output",
        "Impact per Excellence",
        "Citation Velocity",
    ]

    selected_kpi = st.selectbox("Choose KPI", kpi_options)

    st.markdown(f"## 📊 KPI Visualization — **{selected_kpi}**")

    kpi_sorted = filtered.sort_values(selected_kpi, ascending=False)

    # ============================================================
    #                    KPI BAR CHART
    # ============================================================

    fig1 = px.bar(
        kpi_sorted,
        x="Name",
        y=selected_kpi,
        color=selected_kpi,
        color_continuous_scale="Viridis",
        title=f"{selected_kpi} — Comparison Across Countries",
    )
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

    # ============================================================
    #                    KPI PIE CHART (RATE KPIs)
    # ============================================================

    st.markdown("## 🥧 KPI Distribution (If Applicable)")

    RATE_KPIS = [
        "Excellence Rate (Top 1%)",
        "High Impact Rate (Top 10%)",
        "Citation Dominance",
    ]

    if selected_kpi in RATE_KPIS:

        # For percentage KPIs → scale to percentage
        df_pie = kpi_sorted.copy()

        if selected_kpi == "Citation Dominance":
            df_pie["value"] = df_pie[selected_kpi] * 100
        else:
            df_pie["value"] = df_pie[selected_kpi] * 100

        fig2 = px.pie(
            df_pie,
            names="Name",
            values="value",
            title=f"{selected_kpi} — Percentage Contribution",
            hole=0.4,
        )
        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("Pie chart not applicable for this KPI (not a %-based metric).")

    # ============================================================
    #                    KPI TABLE — LEADERBOARD
    # ============================================================

    st.markdown("## 🏆 KPI Leaderboard")

    leaderboard = kpi_sorted[["Name", selected_kpi]]
    st.dataframe(leaderboard, use_container_width=True)

    # ============================================================
    #                      KPI RANK VISUALIZATION
    # ============================================================

    st.markdown("## 📉 Ranking Based on KPI")

    kpi_sorted["Rank Position"] = range(1, len(kpi_sorted) + 1)

    fig_rank = px.bar(
        kpi_sorted,
        x="Name",
        y="Rank Position",
        title=f"Ranking by {selected_kpi}",
        color="Rank Position",
        color_continuous_scale="bluered_r",
    )
    fig_rank.update_yaxes(autorange="reversed")  # Rank 1 on top
    fig_rank.update_layout(showlegend=False)

    st.plotly_chart(fig_rank, use_container_width=True)

    # ============================================================
    #                     KPI DEFINITIONS + INSIGHTS
    # ============================================================

    st.markdown("## 🔍 KPI Meaning & Interpretation")

    KPI_DEFINITIONS = {
        "Citation Efficiency": "Measures citations per publication. High values = strong influence per paper.",
        "Excellence Rate (Top 1%)": "% of publications in the world’s top 1% most cited category.",
        "High Impact Rate (Top 10%)": "% of publications in the global top 10% most cited papers.",
        "Citation Quality Index": "Combines CNCI with citation efficiency to measure true impact quality.",
        "Collaboration Advantage": "Impact benefit gained from international collaboration.",
        "Rank Efficiency": "Documents produced per rank position (lower rank better).",
        "Citation Dominance": "Share of total global citation volume.",
        "Quality Weighted Output": "Publications weighted by normalized citation impact (CNCI).",
        "Impact per Excellence": "Citations per Top-10% paper.",
        "Citation Velocity": "Citations per year since publication; shows growth speed.",
    }

    st.info(f"**{selected_kpi}** — {KPI_DEFINITIONS[selected_kpi]}")

    # ============================================================
    #                  AUTOMATED KPI INSIGHTS
    # ============================================================

    st.markdown("## 🧠 Automated Insights")

    top_row = kpi_sorted.iloc[0]
    bottom_row = kpi_sorted.iloc[-1]

    st.write(f"""
### 🥇 Top Performer
- **{top_row['Name']}** ranks #1 in **{selected_kpi}**
- Value: **{top_row[selected_kpi]:,.3f}**

### 🥈 Lowest Performer
- **{bottom_row['Name']}** ranks last in **{selected_kpi}**
- Value: **{bottom_row[selected_kpi]:,.3f}**

### 📌 Interpretation
- Higher values in this KPI indicate superior research strength in this dimension.
- Lower values indicate need for improvement, strategic investments, or collaboration.
""")

    st.markdown("---")


# ======================================================================
#              PAGE 4 — DRILLTHROUGH DASHBOARD (FULL WORKING)
# ======================================================================

elif page == "🎯 Country Drillthrough Dashboard":

    st.title("🎯 Drillthrough Dashboard — Country Deep Dive")
    st.markdown("""
A detailed scientometric profile of any selected country including productivity,
impact, excellence, efficiency, collaboration and year-based trends.
""")

    # =========================================================
    #               COUNTRY SELECTION
    # =========================================================
    if "Name" not in filtered.columns:
        st.error("Column 'Name' is missing from dataset. Cannot generate drillthrough.")
        st.stop()

    country_list = sorted(filtered["Name"].unique())

    if len(country_list) == 0:
        st.warning("No countries available in filtered dataset.")
        st.stop()

    selected_country = st.selectbox("Select a Country", country_list)

    sub = filtered[filtered["Name"] == selected_country]

    if len(sub) == 0:
        st.warning("No data available for this country.")
        st.stop()

    row = sub.iloc[0]  # for KPI cards

    # =========================================================
    #                          KPI CARDS
    # =========================================================
    st.markdown("## 📌 Key Scientometric Indicators")

    k1, k2, k3, k4 = st.columns(4)
    k5, k6, k7, k8 = st.columns(4)

    def metric_card(title, value):
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric(title, value)
        st.markdown("</div>", unsafe_allow_html=True)

    with k1: metric_card("Documents", f"{int(row['Web of Science Documents']):,}")
    with k2: metric_card("Citations", f"{int(row['Times Cited']):,}")
    with k3: metric_card("CNCI", round(row["Category Normalized Citation Impact"], 3))
    with k4: metric_card("Rank", int(row["Rank"]))

    with k5: metric_card("Citation Efficiency", round(row["Citation Efficiency"], 3))
    with k6: metric_card("Top 1% Papers", int(row["Documents in Top 1%"]))
    with k7: metric_card("Top 10% Papers", int(row["Documents in Top 10%"]))
    with k8: metric_card("Collab-CNCI", round(row["Collab-CNCI"], 3))

    st.markdown("---")

    # =========================================================
    #                     EXCELLENCE PIE CHART
    # =========================================================
    st.markdown("## 🏆 Excellence Contribution — Top 1% vs Top 10%")

    ex_df = pd.DataFrame({
        "Category": ["Top 1% Papers", "Top 10% Papers"],
        "Count": [
            int(row["Documents in Top 1%"]),
            int(row["Documents in Top 10%"])
        ]
    })

    fig_pie = px.pie(
        ex_df,
        names="Category",
        values="Count",
        hole=0.45,
        color="Category",
        title="Excellence Distribution",
        color_discrete_map={
            "Top 1% Papers": "#00e3aa",
            "Top 10% Papers": "#3dbbff"
        }
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # =========================================================
    #                   YEAR TREND CHARTS
    # =========================================================
    st.markdown("## 📈 Yearly Research Trend")

    trend_df = filtered[filtered["Name"] == selected_country][["year", "Web of Science Documents", "Times Cited"]]

    if trend_df["year"].nunique() > 1:

        cA, cB = st.columns(2)

        with cA:
            st.subheader("Yearly Document Trend")
            fig_docs = px.line(
                trend_df,
                x="year",
                y="Web of Science Documents",
                markers=True,
                color_discrete_sequence=["#57a6ff"],
                title="Documents Over Years"
            )
            st.plotly_chart(fig_docs, use_container_width=True)

        with cB:
            st.subheader("Yearly Citation Trend")
            fig_cites = px.line(
                trend_df,
                x="year",
                y="Times Cited",
                markers=True,
                color_discrete_sequence=["#ff6b7b"],
                title="Citations Over Years"
            )
            st.plotly_chart(fig_cites, use_container_width=True)

    else:
        st.info("Only one year of data available — cannot show trend charts.")

    st.markdown("---")

    # =========================================================
    #                  CITATION DISTRIBUTION DONUT
    # =========================================================
    st.markdown("## 🍩 Citation Distribution Breakdown")

    citation_df = pd.DataFrame({
        "Category": ["Total Citations", "Quality Weighted Output"],
        "Value": [row["Times Cited"], row["Quality Weighted Output"]]
    })

    fig_donut = px.pie(
        citation_df,
        names="Category",
        values="Value",
        hole=0.55,
        title="Citation Distribution",
        color_discrete_sequence=["#ffb366", "#9a6bff"]
    )
    st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")

    # =========================================================
    #                     MULTI-METRIC BAR CHART
    # =========================================================
    st.markdown("## 📊 Research Strength Indicators")

    comp_df = pd.DataFrame({
        "Metric": ["Citation Efficiency", "CNCI", "Collab-CNCI", "Impact per Excellence"],
        "Value": [
            row["Citation Efficiency"],
            row["Category Normalized Citation Impact"],
            row["Collab-CNCI"],
            row["Impact per Excellence"],
        ]
    })

    fig_comp = px.bar(
        comp_df,
        x="Metric",
        y="Value",
        color="Value",
        color_continuous_scale="viridis",
        title=f"{selected_country} — Multi-Dimensional Performance"
    )
    fig_comp.update_layout(showlegend=False)
    st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("---")

    # =========================================================
    #               COUNTRY RANK COMPARISON TABLE
    # =========================================================
    st.markdown("## 📉 Ranking Context (Compared to Others)")

    rank_df = filtered[["Name", "Rank", "Times Cited", "Web of Science Documents", "Category Normalized Citation Impact"]]
    st.dataframe(rank_df.sort_values("Rank"), use_container_width=True)

    st.markdown("---")

    # =========================================================
    #                     FINAL INSIGHTS
    # =========================================================
    st.markdown("## 🔍 Final Insights")

    st.write(f"""
### 🔹 Summary for **{selected_country}**
- **Documents:** {row['Web of Science Documents']:,}
- **Citations:** {row['Times Cited']:,}
- **CNCI:** {round(row['Category Normalized Citation Impact'], 3)}
- **Top 1% Papers:** {row['Documents in Top 1%']}
- **Top 10% Papers:** {row['Documents in Top 10%']}
- **Citation Efficiency:** {round(row['Citation Efficiency'], 2)}
- **Collab-CNCI:** {round(row['Collab-CNCI'], 2)}

### 🧠 Interpretation
- High CNCI → Strong international impact.
- High Top 1% and Top 10% → Research excellence.
- High collaboration advantage → Strong partnerships.
""")

    st.success("Drillthrough analysis generated successfully.")
