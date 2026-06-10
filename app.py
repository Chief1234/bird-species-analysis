import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="🐦 Bird Species Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🐦 Bird Species Observation Analysis")
st.markdown("*Comparing Forest vs Grassland habitats across 11 National Parks*")

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    engine = create_engine('sqlite:///data/bird_data.db')
    return pd.read_sql("SELECT * FROM bird_observations", con=engine)

df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
st.sidebar.header("🔎 Filters")

habitat_filter = st.sidebar.multiselect(
    "Select Habitat",
    options=df['Location_Type'].unique(),
    default=df['Location_Type'].unique()
)

admin_filter = st.sidebar.multiselect(
    "Select Admin Unit",
    options=df['Admin_Unit_Code'].unique(),
    default=df['Admin_Unit_Code'].unique()
)

year_filter = st.sidebar.multiselect(
    "Select Year",
    options=sorted(df['Year'].unique()),
    default=sorted(df['Year'].unique())
)

# Apply filters
filtered_df = df[
    (df['Location_Type'].isin(habitat_filter)) &
    (df['Admin_Unit_Code'].isin(admin_filter)) &
    (df['Year'].isin(year_filter))
]

# ─────────────────────────────────────────────
# KEY METRICS (TOP CARDS)
# ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Observations", f"{len(filtered_df):,}")
col2.metric("Unique Species", filtered_df['Scientific_Name'].nunique())
col3.metric("Admin Units", filtered_df['Admin_Unit_Code'].nunique())
col4.metric("At-Risk Species", int(filtered_df['PIF_Watchlist_Status'].sum()))

st.divider()

# ─────────────────────────────────────────────
# ROW 1: SPECIES CHARTS
# ─────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("🏆 Top 15 Most Observed Species")
    top15 = filtered_df['Common_Name'].value_counts().head(15).reset_index()
    top15.columns = ['Species', 'Count']
    fig1 = px.bar(top15, x='Count', y='Species', orientation='h',
                  color='Count', color_continuous_scale='Teal',
                  title="Species Observation Count")
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("🌍 Species Count by Habitat")
    hab_species = filtered_df.groupby('Location_Type')['Scientific_Name'].nunique().reset_index()
    hab_species.columns = ['Habitat', 'Unique Species']
    fig2 = px.pie(hab_species, names='Habitat', values='Unique Species',
                  color_discrete_sequence=['#2ecc71', '#3498db'],
                  title="Species Diversity: Forest vs Grassland")
    st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
# ROW 2: TEMPORAL ANALYSIS
# ─────────────────────────────────────────────
st.subheader("📅 Observations Over Time")

col_c, col_d = st.columns(2)

with col_c:
    yearly_data = filtered_df.groupby(['Year', 'Location_Type']).size().reset_index(name='Count')
    fig3 = px.line(yearly_data, x='Year', y='Count', color='Location_Type',
                   markers=True, title="Yearly Observation Trend",
                   color_discrete_sequence=['#27ae60', '#2980b9'])
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    season_order = ['Spring', 'Summer', 'Autumn', 'Winter']
    seasonal_data = filtered_df.groupby(['Season', 'Location_Type']).size().reset_index(name='Count')
    fig4 = px.bar(seasonal_data, x='Season', y='Count', color='Location_Type',
                  barmode='group', category_orders={'Season': season_order},
                  title="Seasonal Bird Activity",
                  color_discrete_sequence=['#27ae60', '#2980b9'])
    st.plotly_chart(fig4, use_container_width=True)

# ─────────────────────────────────────────────
# ROW 3: ENVIRONMENTAL ANALYSIS
# ─────────────────────────────────────────────
st.subheader("🌤️ Environmental Conditions")

col_e, col_f = st.columns(2)

with col_e:
    fig5 = px.scatter(filtered_df.sample(min(2000, len(filtered_df))),
                      x='Temperature', y='Humidity',
                      color='Location_Type', opacity=0.5,
                      title="Temperature vs Humidity by Habitat",
                      color_discrete_sequence=['#27ae60', '#2980b9'])
    st.plotly_chart(fig5, use_container_width=True)

with col_f:
    id_data = filtered_df['ID_Method'].value_counts().reset_index()
    id_data.columns = ['Method', 'Count']
    fig6 = px.pie(id_data, names='Method', values='Count',
                  title="Identification Methods Used",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig6, use_container_width=True)

# ─────────────────────────────────────────────
# ROW 4: CONSERVATION INSIGHTS
# ─────────────────────────────────────────────
st.subheader("⚠️ Conservation Insights")

col_g, col_h = st.columns(2)

with col_g:
    watchlist_df = filtered_df[filtered_df['PIF_Watchlist_Status'] == True]
    if len(watchlist_df) > 0:
        wl_species = watchlist_df['Common_Name'].value_counts().head(10).reset_index()
        wl_species.columns = ['Species', 'Count']
        fig7 = px.bar(wl_species, x='Species', y='Count',
                      title="⚠️ At-Risk Species (PIF Watchlist)",
                      color='Count', color_continuous_scale='Reds')
        fig7.update_xaxes(tickangle=45)
        st.plotly_chart(fig7, use_container_width=True)
    else:
        st.info("No watchlist species in current filter selection.")

with col_h:
    admin_counts = filtered_df.groupby('Admin_Unit_Code').size().reset_index(name='Observations')
    fig8 = px.bar(admin_counts.sort_values('Observations', ascending=False),
                  x='Admin_Unit_Code', y='Observations',
                  title="Observations per Admin Unit",
                  color='Observations', color_continuous_scale='Viridis')
    st.plotly_chart(fig8, use_container_width=True)

# ─────────────────────────────────────────────
# RAW DATA TABLE
# ─────────────────────────────────────────────
st.subheader("📋 Raw Data Explorer")
st.dataframe(
    filtered_df[['Date', 'Location_Type', 'Admin_Unit_Code', 'Common_Name',
                 'Scientific_Name', 'ID_Method', 'Distance', 'Temperature',
                 'Humidity', 'PIF_Watchlist_Status']].head(100),
    use_container_width=True
)