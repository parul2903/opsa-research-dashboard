# ======================================================================
#          GLOBAL RESEARCH ANALYTICS DASHBOARD (SIMPLIFIED & CLEAN)
#                      POWER BI DARK THEME – FINAL VERSION
# ======================================================================

import os, sys, warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------
# FIX IMPORT PATH FOR src/
# ----------------------------------------------------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.load_data import load_dataset

# ======================================================================
#                      STREAMLIT CONFIG + THEME
# ======================================================================
st.set_page_config(
    page_title="Global Research Dashboard",
    layout="wide",
    page_icon="📊"
)

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
h1, h2, h3 {
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
#                    GLOBAL METRIC CARD FUNCTION
# ======================================================================
def metric_card(title, value):
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric(title, value)
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================================
#                           LOAD DATA
# ======================================================================
DATA_PATH = os.path.join(ROOT, "data", "publications.csv")
df = load_dataset(DATA_PATH)
df = df.loc[:, ~df.columns.duplicated()].copy()

# ======================================================================
#                       KPI CALCULATIONS
# ======================================================================
df["Citation Efficiency"] = df["Times Cited"] / df["Web of Science Documents"]
df["High Impact Rate (Top 10%)"] = df["Documents in Top 10%"] / df["Web of Science Documents"]
df["Excellence Rate (Top 1%)"] = df["Documents in Top 1%"] / df["Web of Science Documents"]
df["Quality Weighted Output"] = df["Web of Science Documents"] * df["Category Normalized Citation Impact"]
df["Collaboration Strength"] = df["Collab-CNCI"]
df["Impact Score"] = df["Times Cited"] * df["Category Normalized Citation Impact"]


# ======================================================================
#                           SIDEBAR
# ======================================================================
st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Go To:",
    ["🏠 Executive Overview", "🎯 Country Drillthrough"]
)

st.sidebar.title("🎛 Global Filters")


# ======================================================================
# 1️⃣ SEARCH FILTER
# ======================================================================
search_term = st.sidebar.text_input("🔍 Search Country")


# ======================================================================
# 2️⃣ COUNTRY FILTER (WITH 'ALL' OPTION)
# ======================================================================

country_list = sorted(df["Name"].unique())
country_options = ["All"] + country_list

selected_countries = st.sidebar.multiselect(
    "🌍 Select Countries",
    options=country_options,
    default=["All"]
)

if len(selected_countries) == 0:
    # Nothing selected → Use All
    final_countries = country_list
elif "All" in selected_countries:
    # User selected All
    final_countries = country_list
else:
    # User selected specific countries
    final_countries = selected_countries



# ======================================================================
# 3️⃣ YEAR FILTER (WITH 'ALL' OPTION)
# ======================================================================

year_list = sorted(df["year"].unique())
year_options = ["All"] + [str(y) for y in year_list]

selected_years = st.sidebar.multiselect(
    "📅 Select Years",
    options=year_options,
    default=["All"]
)

if len(selected_years) == 0:
    final_years = year_list
elif "All" in selected_years:
    final_years = year_list
else:
    final_years = [int(y) for y in selected_years]



# ======================================================================
# 4️⃣ APPLY FILTERS
# ======================================================================
filtered = df.copy()

# Search filter
if search_term:
    filtered = filtered[
        filtered["Name"].str.contains(search_term, case=False, na=False)
    ]

# Apply country filter
filtered = filtered[filtered["Name"].isin(final_countries)]

# Apply year filter
filtered = filtered[filtered["year"].isin(final_years)]

st.sidebar.success(f"Rows after filtering: {len(filtered)}")


# ======================================================================
#                 PAGE 1 — EXECUTIVE OVERVIEW
# ======================================================================
if page == "🏠 Executive Overview":

    st.title("🏠 Executive Overview")
    st.markdown("A clean, executive summary of global research productivity and impact.")

    # ===========================
    # KPI CARDS
    # ===========================
    st.markdown("## 📌 Key Indicators")

    c1, c2, c3, c4 = st.columns(4)

    def metric_card(title, val):
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric(title, val)
        st.markdown("</div>", unsafe_allow_html=True)

    with c1:
        metric_card("Total Documents", f"{filtered['Web of Science Documents'].sum():,}")
    with c2:
        metric_card("Total Citations", f"{filtered['Times Cited'].sum():,}")
    with c3:
        metric_card("Avg CNCI", round(filtered["Category Normalized Citation Impact"].mean(), 2))
    with c4:
        metric_card("Avg Top 10% Rate", f"{round(filtered['High Impact Rate (Top 10%)'].mean()*100, 2)}%")

    st.markdown("---")

    # ===========================
    # MAIN CHARTS (4)
    # ===========================
    st.markdown("## 📊 Core Scientometric Charts")

    colA, colB = st.columns(2)

    # Documents
    with colA:
        docs = (
            filtered.groupby("Name")["Web of Science Documents"]
            .sum().reset_index().sort_values("Web of Science Documents", ascending=False)
        )
        figA = px.bar(
            docs, x="Name", y="Web of Science Documents",
            color="Web of Science Documents",
            color_continuous_scale="Blues",
            title="Documents by Country"
        )
        figA.update_layout(showlegend=False)
        st.plotly_chart(figA, use_container_width=True)

    # Citations
    with colB:
        cites = (
            filtered.groupby("Name")["Times Cited"]
            .sum().reset_index().sort_values("Times Cited", ascending=False)
        )
        figB = px.bar(
            cites, x="Name", y="Times Cited",
            color="Times Cited",
            color_continuous_scale="Purples",
            title="Citations by Country"
        )
        figB.update_layout(showlegend=False)
        st.plotly_chart(figB, use_container_width=True)

    st.markdown("---")

    # CNCI + Top 10% row
    colC, colD = st.columns(2)

    with colC:
        figC = px.bar(
            filtered.sort_values("Category Normalized Citation Impact", ascending=False),
            x="Name", y="Category Normalized Citation Impact",
            color="Category Normalized Citation Impact",
            color_continuous_scale="Viridis",
            title="CNCI — Research Quality"
        )
        figC.update_layout(showlegend=False)
        st.plotly_chart(figC, use_container_width=True)

    with colD:
        figD = px.bar(
            filtered.sort_values("Documents in Top 10%", ascending=False),
            x="Name", y="Documents in Top 10%",
            color="Documents in Top 10%",
            color_continuous_scale="Burgyl",
            title="Top 10% Papers — Research Excellence"
        )
        figD.update_layout(showlegend=False)
        st.plotly_chart(figD, use_container_width=True)

    # ===========================
    # YEAR-WISE TOP 5 BAR (SLIDER STYLE)
    # ===========================
    st.markdown("## 🏆 Top 5 Countries by Documents — Year Wise")

    # Aggregate by year + country
    year_grouped = (
        filtered.groupby(["year", "Name"])["Web of Science Documents"]
        .sum()
        .reset_index()
    )

    # Plot using slider
    fig_year_top5 = px.bar(
        year_grouped.sort_values(["year", "Web of Science Documents"], ascending=[True, False]),
        x="Web of Science Documents",
        y="Name",
        animation_frame="year",
        orientation="h",
        title="Top 5 Countries Each Year (Documents)",
        range_x=[0, year_grouped["Web of Science Documents"].max() * 1.1],
        color="Web of Science Documents",
        color_continuous_scale="Blues"
    )

    # Only keep top 5 per year
    fig_year_top5.update_traces(
        selector=dict(type="bar"),
        width=0.7
    )

    # Update layout
    fig_year_top5.update_layout(
        yaxis={'categoryorder':'total ascending'},
        showlegend=False,
        height=600
    )

    # Display chart
    st.plotly_chart(fig_year_top5, use_container_width=True)


    st.markdown("---")

    

    # ===========================
    # PIE CHART — CITATION SHARE
    # ===========================
    st.markdown("## 🍩 Global Citation Share")

    pie_df = (
        filtered.groupby("Name")["Times Cited"]
        .sum().reset_index()
    )
    fig_pie = px.pie(
        pie_df,
        names="Name",
        values="Times Cited",
        hole=0.45,
        title="Share of Global Citations"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # ===========================
    # SUMMARY TABLE
    # ===========================
    st.markdown("## 📄 Summary Table")

    summary_df = filtered[[
        "Name", "Web of Science Documents", "Times Cited",
        "Category Normalized Citation Impact", "Documents in Top 10%",
        "Citation Efficiency"
    ]].sort_values("Times Cited", ascending=False)

    st.dataframe(summary_df, use_container_width=True)

    st.markdown("---")

    # ===========================
    # INSIGHTS
    # ===========================
    st.markdown("## 🔍 Key Insights")
    st.write("""
- Countries with high CNCI show superior research quality.
- High Top 10% output highlights excellence.
- Citations show scientific influence more strongly than document count.
- Switzerland and the UK show strong impact despite moderate publication volume.
""")


# ======================================================================
#                  PAGE 2 — DRILLTHROUGH DASHBOARD
# ======================================================================
elif page == "🎯 Country Drillthrough":

    st.title("🎯 Country Drillthrough Dashboard")
    st.markdown("Deep-dive into a single country’s scientific performance.")

    # ---------------------------
    # Select Country
    # ---------------------------
    country_list = sorted(filtered["Name"].unique())
    selected_country = st.selectbox("Select Country", country_list)

    sub = filtered[filtered["Name"] == selected_country]

    # ---------------------------
    # Pull a representative row
    # ---------------------------
    row = sub.iloc[0]

    # ===========================
    # KPI CARDS
    # ===========================
    st.markdown("## 📌 Key Indicators")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Documents", f"{int(row['Web of Science Documents']):,}")

    with c2:
        metric_card("Citations", f"{int(row['Times Cited']):,}")

    with c3:
        metric_card("CNCI", round(row["Category Normalized Citation Impact"], 3))

    with c4:
        metric_card("Top 10% Papers", int(row["Documents in Top 10%"]))

    st.markdown("---")

    # ===========================
    # PIE — Excellence Breakdown
    # ===========================
    st.markdown("## 🏆 Excellence Breakdown")

    ex_df = pd.DataFrame({
        "Category": ["Top 1% Papers", "Top 10% Papers"],
        "Count": [
            int(row["Documents in Top 1%"]),
            int(row["Documents in Top 10%"])
        ]
    })

    fig_ex = px.pie(ex_df, names="Category", values="Count", hole=0.5)
    st.plotly_chart(fig_ex, use_container_width=True)

    st.markdown("---")

    # ===========================
    # AVG YEAR-WISE TRENDS (GLOBAL VS COUNTRY)
    # ===========================

    trend_df = filtered[filtered["Name"] == selected_country]

    if trend_df["year"].nunique() > 1:

        st.markdown("## 📈 Year-Wise Average Trends (Global vs Country)")
        colA, colB = st.columns(2)

        # ---- Global/Filtered Year-Wise Averages ----
        avg_year_df = (
            filtered.groupby("year")[["Web of Science Documents", "Times Cited"]]
            .mean()
            .reset_index()
        )
        avg_year_df["Country"] = "Global Average"

        # ---- Selected Country Year-Wise ----
        country_year_df = (
            sub.groupby("year")[["Web of Science Documents", "Times Cited"]]
            .mean()
            .reset_index()
        )
        country_year_df["Country"] = selected_country

        # -----------------------------
        # DOCUMENTS AVG LINE CHART
        # -----------------------------
        with colA:
            fig_avg_docs = px.line(
                avg_year_df,
                x="year",
                y="Web of Science Documents",
                markers=True,
                title="Avg Documents per Year (Global vs Country)",
                color="Country",
                color_discrete_sequence=["#4cb4ff"]
            )

            # Add country line
            fig_avg_docs.add_scatter(
                x=country_year_df["year"],
                y=country_year_df["Web of Science Documents"],
                mode="lines+markers",
                name=f"{selected_country} Documents",
                line=dict(color="#ffa600", width=3)
            )

            st.plotly_chart(fig_avg_docs, use_container_width=True)

        # -----------------------------
        # CITATIONS AVG LINE CHART
        # -----------------------------
        with colB:
            fig_avg_cites = px.line(
                avg_year_df,
                x="year",
                y="Times Cited",
                markers=True,
                title="Avg Citations per Year (Global vs Country)",
                color="Country",
                color_discrete_sequence=["#4cb4ff"]
            )

            fig_avg_cites.add_scatter(
                x=country_year_df["year"],
                y=country_year_df["Times Cited"],
                mode="lines+markers",
                name=f"{selected_country} Citations",
                line=dict(color="#ffa600", width=3)
            )

            st.plotly_chart(fig_avg_cites, use_container_width=True)

    else:
        st.info("Not enough years to display trend.")

    st.markdown("---")

    # ===========================
    # YEAR-WISE TABLE
    # ===========================
    st.markdown("## 📅 Year-Wise Performance Table")

    table_cols = [
        "year",
        "Web of Science Documents",
        "Times Cited",
        "Category Normalized Citation Impact",
        "Documents in Top 10%",
        "Documents in Top 1%",
        "Citation Efficiency",
        "Collab-CNCI"
    ]

    year_table = sub[table_cols].sort_values("year")

    st.dataframe(
        year_table,
        use_container_width=True,
        height=350
    )

    st.markdown("---")

    # ===========================
    # Multi-Metric Strength Indicators
    # ===========================
    st.markdown("## 📊 Performance Strength Indicators")

    performance_df = pd.DataFrame({
        "Metric": ["Citation Efficiency", "CNCI", "Collab-CNCI"],
        "Value": [
            row["Citation Efficiency"],
            row["Category Normalized Citation Impact"],
            row["Collab-CNCI"]
        ]
    })

    fig_perf = px.bar(
        performance_df,
        x="Metric",
        y="Value",
        color="Value",
        color_continuous_scale="viridis",
        title=f"{selected_country} — Research Strength Profile"
    )

    fig_perf.update_layout(showlegend=False)
    st.plotly_chart(fig_perf, use_container_width=True)

    st.markdown("---")

    # ===========================
    # FINAL INSIGHTS
    # ===========================
    st.markdown("## 🔍 Key Insights")

    st.write(f"""
- **{selected_country}** produced **{row['Web of Science Documents']:,}** documents  
  and received **{row['Times Cited']:,}** citations.

- CNCI of **{round(row['Category Normalized Citation Impact'], 2)}** shows research
  quality relative to the world baseline (1 = world average).

- Top 10% paper output of **{int(row['Documents in Top 10%'])}** reflects excellence.

- Collaboration strength of **{round(row['Collab-CNCI'], 2)}** indicates how strongly
  international collaboration boosts research impact.
""")

    st.success("Drillthrough analysis generated successfully!")
