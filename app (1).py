"""
Global Literacy & Education Trends: An Analytical Study
Phase 8: Production-Grade Interactive Streamlit Dashboard Engine
"""

import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. Page Configuration & UI Theme setup
st.set_page_config(
    page_title="Global Education & Literacy Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "education_trends_analytics.db"

# Cache database connection for high performance
@st.cache_data
def fetch_db_data(query: str) -> pd.DataFrame:
    """Executes safe read transactions against the analytical SQLite database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as db_err:
        st.error(f"Database Query Fault: {db_err}")
        return pd.DataFrame()

# --- Load Master Metadata Fields for Filter Options ---
countries_df = fetch_db_data("SELECT DISTINCT country FROM literacy_master ORDER BY country;")
all_countries = countries_df['country'].tolist() if not countries_df.empty else ["Global"]

# -------------------------------------------------------------------------
# SIDEBAR CONTROL PIPELINE
# -------------------------------------------------------------------------
st.sidebar.markdown("## ⚙️ Analytics Control Unit")
st.sidebar.info("Filter the dynamic relational visualizations across global vectors.")

# Country Filter Vector
selected_country = st.sidebar.selectbox(
    "Select Target Country/Region:",
    options=["All Countries"] + all_countries,
    index=0
)

# Historical Timeline Slider Scope
year_range = st.sidebar.slider(
    "Select Analysis Window Bounds (Years):",
    min_value=1990,
    max_value=2023,
    value=(2000, 2020),
    step=1
)

st.sidebar.markdown("---")
st.sidebar.success("💡 System Core: Live Feed Connected")

# -------------------------------------------------------------------------
# MAIN PRESENTATION LAYER
# -------------------------------------------------------------------------
st.title("🎓 Global Literacy & Socio-Economic Trends Analytics")
st.markdown("A unified intelligence dashboard mapping education trajectories, gender parity gaps, and economic returns from 1990 to recent records.")

# Constructing Dynamic SQL predicates based on filters
query_condition = f"WHERE year BETWEEN {year_range[0]} AND {year_range[1]}"
if selected_country != "All Countries":
    query_condition += f" AND country = '{selected_country}'"

# Fetch active frames based on dashboard context scope
lm_query = f"SELECT * FROM literacy_master {query_condition};"
se_query = f"SELECT * FROM socio_economic_metrics {query_condition};"

df_lit = fetch_db_data(lm_query)
df_se = fetch_db_data(se_query)

# -------------------------------------------------------------------------
# TOP TIER: HIGH-LEVEL EXECUTIVE METRICS (KPI CARDS)
# -------------------------------------------------------------------------
if not df_lit.empty:
    st.markdown("### 📈 Key Performance Indicators (KPIs)")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    # Calculate weighted mean snapshots for the current viewport scope
    avg_adult_lit = df_lit['adult_literacy_rate'].mean()
    avg_gender_gap = df_lit['literacy_gender_gap'].mean()

    avg_gdp = df_se['gdp_per_capita'].mean() if not df_se.empty else 0.0
    avg_schooling = df_se['avg_years_of_schooling'].mean() if not df_se.empty else 0.0

    kpi_col1.metric(label="Avg Adult Literacy", value=f"{avg_adult_lit:.2f} %")
    kpi_col2.metric(label="Gender Gap (M vs F)", value=f"{avg_gender_gap:.2f} pp", delta=f"{'-' if avg_gender_gap > 5 else 'Stable'}", delta_color="inverse")
    kpi_col3.metric(label="Avg Schooling Duration", value=f"{avg_schooling:.1f} Years")
    kpi_col4.metric(label="Avg GDP Per Capita", value=f"${avg_gdp:,.2f}")
    st.markdown("---")

# -------------------------------------------------------------------------
# INTERACTIVE TABS INTERFACE SYSTEM
# -------------------------------------------------------------------------
tab_trends, tab_economics, tab_explorer = st.tabs([
    "📈 Literacy & Gender Trend Analysis",
    "💰 Socio-Economic Performance",
    "🗄️ Relational Database Explorer"
])

# --- TAB 1: LITERACY & GENDER TREND ANALYSIS ---
with tab_trends:
    st.subheader("Historical Timeline Paths & Gender Parity Frameworks")

    if df_lit.empty:
        st.warning("No tracking records matched the chosen filter scope parameters.")
    else:
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("#### Adult Literacy Trajectory over Time")
            fig, ax = plt.subplots(figsize=(6, 3.8))

            if selected_country == "All Countries":
                # Show top 5 performing countries in this window for clean clarity
                top_countries = df_lit.groupby('country')['adult_literacy_rate'].mean().nlargest(5).index
                df_sub = df_lit[df_lit['country'].isin(top_countries)]
                sns.lineplot(data=df_sub, x='year', y='adult_literacy_rate', hue='country', marker='o', ax=ax)
                ax.set_title("Top 5 Countries Performance Trends")
            else:
                sns.lineplot(data=df_lit, x='year', y='adult_literacy_rate', color='teal', marker='o', linewidth=2.5, ax=ax)
                ax.set_title(f"{selected_country}: Adult Literacy Curve")

            ax.set_ylabel("Literacy Rate (%)")
            ax.set_xlabel("Year")
            st.pyplot(fig)

        with col_chart2:
            st.markdown("#### Youth Literacy Profile: Male vs Female Gap")
            fig, ax = plt.subplots(figsize=(6, 3.8))

            if selected_country != "All Countries":
                # Line chart comparison for single country selection
                df_melted = df_lit.melt(id_vars=['year'], value_vars=['youth_literacy_rate_male', 'youth_literacy_rate_female'],
                                        var_name='Gender Parameter', value_name='Rate')
                df_melted['Gender Parameter'] = df_melted['Gender Parameter'].map({
                    'youth_literacy_rate_male': 'Male Youth', 'youth_literacy_rate_female': 'Female Youth'
                })
                sns.lineplot(data=df_melted, x='year', y='Rate', hue='Gender Parameter', palette=['#1f77b4', '#e377c2'], marker='s', ax=ax)
                ax.set_title(f"Gender Segregated Paths for {selected_country}")
            else:
                # Distribution plot for all countries context
                sns.histplot(data=df_lit, x='literacy_gender_gap', kde=True, color='crimson', ax=ax)
                ax.set_title("Global Density Distribution of Literacy Gender Gaps")
                ax.set_xlabel("Gap Points (Male - Female)")

            st.pyplot(fig)

# --- TAB 2: SOCIO-ECONOMIC PERFORMANCE ---
with tab_economics:
    st.subheader("Evaluating Economic Returns vs Educational Ingestion Indexes")

    if df_se.empty:
        st.warning("Socio-economic dimensions data array missing or disconnected.")
    else:
        col_ec1, col_ec2 = st.columns([3, 2])

        with col_ec1:
            st.markdown("#### The Learning Return Vector: Schooling vs Wealth Indices")
            fig, ax = plt.subplots(figsize=(7, 4))

            # Scatter query evaluation
            latest_year = df_se['year'].max()
            df_slice = df_se[df_se['year'] == latest_year]

            sns.scatterplot(
                data=df_slice if selected_country == "All Countries" else df_se,
                x='avg_years_of_schooling',
                y='gdp_per_capita',
                hue='education_index' if selected_country == "All Countries" else 'year',
                palette='viridis',
                size='education_index',
                sizes=(40, 300),
                alpha=0.8,
                ax=ax
            )
            ax.set_title(f"Cross-Sectional Wealth Mapping (Reference Scope Scope Context)")
            ax.set_xlabel("Average Years of Schooling")
            ax.set_ylabel("GDP Per Capita ($)")
            st.pyplot(fig)

        with col_ec2:
            st.markdown("#### Structural Data Insights Table")
            display_cols = ['country', 'year', 'gdp_per_capita', 'avg_years_of_schooling', 'education_index']
            valid_cols = [c for c in display_cols if c in df_se.columns]
            st.dataframe(
                df_se[valid_cols].sort_values(by=['education_index', 'gdp_per_capita'], ascending=False).head(100),
                use_container_width=True,
                height=300
            )

# --- TAB 3: RELATIONAL DATABASE EXPLORER ---
with tab_explorer:
    st.subheader("🏛️ Direct Relational Database Query Console")
    st.markdown("Run custom analytical SQL inquiries instantly against the structured SQLite storage engine layer tables.")

    st.caption("Available Live Architecture Tables: `literacy_master` | `illiteracy_census` | `socio_economic_metrics`")

    # Custom Query Input Sandbox Area
    default_sandbox_query = """SELECT country, year, adult_literacy_rate
FROM literacy_master
WHERE adult_literacy_rate < 50 AND year = 2020
ORDER BY adult_literacy_rate ASC
LIMIT 10;"""

    user_sql_input = st.text_area("SQL Sandbox Query Input Console:", value=default_sandbox_query, height=120)

    if st.button("⚡ Execute Relational Query Plan", type="primary"):
        with st.spinner("Processing transaction execution parameters..."):
            query_res = fetch_db_data(user_sql_input)
            if not query_res.empty:
                st.success(f"Execution Successful! Fetched {len(query_res)} relational rows.")
                st.dataframe(query_res, use_container_width=True)
            else:
                st.info("Query returned 0 rows or structural fault layout anomaly occurred.")
