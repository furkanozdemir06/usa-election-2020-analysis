import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="US Election 2020 Analytics",
    page_icon="🇺🇸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Glassmorphism Theme)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .metric-card {
        background-color: #1e222d;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 1px solid #2e3440;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Data Loading & Caching
# ---------------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('president_county.csv')
        return df
    except FileNotFoundError:
        # Fallback dummy data if file is missing during preview
        data = {
            'state': ['Delaware', 'Delaware', 'Arizona', 'Arizona', 'Florida'],
            'county': ['Kent County', 'Sussex County', 'Maricopa County', 'Graham County', 'Miami-Dade'],
            'current_votes': [87025, 129352, 2069475, 14996, 1156000],
            'total_votes': [87025, 129352, 2068144, 14996, 1156000],
            'percent': [100, 100, 100, 100, 100]
        }
        return pd.DataFrame(data)

df = load_data()

# ---------------------------------------------------------
# Hero Banner
# ---------------------------------------------------------
st.image(
    "https://images.ft.com/v3/image/raw/https%3A%2F%2Fd1e00ek4ebabms.cloudfront.net%2Fproduction%2F397168c7-e2a5-49f2-80d7-b7fde5dd549e.jpg?source=next-article&fit=scale-down&quality=highest&width=700&dpr=1",
    use_container_width=True
)

st.title("🇺🇸 United States Election 2020 Analysis")
st.caption("An in-depth data analytics dashboard focusing on county-level vote breakdowns, turnout rates, and state distribution.")

st.divider()

# ---------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------
st.sidebar.header("🔍 Filter Options")

selected_states = st.sidebar.multiselect(
    "Select States:",
    options=sorted(df['state'].unique()),
    default=[]
)

if selected_states:
    filtered_df = df[df['state'].isin(selected_states)]
else:
    filtered_df = df.copy()

# ---------------------------------------------------------
# KPI Metrics Section
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

total_votes = filtered_df['total_votes'].sum()
total_counties = filtered_df['county'].nunique()
total_states = filtered_df['state'].nunique()
avg_turnout = filtered_df['percent'].mean()

with col1:
    st.metric(label="Total Votes Counted", value=f"{total_votes:,}")

with col2:
    st.metric(label="States Covered", value=f"{total_states}")

with col3:
    st.metric(label="Total Counties", value=f"{total_counties:,}")

with col4:
    st.metric(label="Avg Reporting Rate", value=f"{avg_turnout:.1f}%")

st.divider()

# ---------------------------------------------------------
# Main Visualizations
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 Analytics Overview", "📋 Raw Data & Search", "📈 Statistical Insights"])

with tab1:
    st.subheader("Top 10 States by Total Votes")
    
    # Aggregating votes by state
    state_votes = filtered_df.groupby('state')['total_votes'].sum().reset_index()
    top10_states = state_votes.sort_values(by='total_votes', ascending=False).head(10)

    fig_bar = px.bar(
        top10_states,
        x='total_votes',
        y='state',
        orientation='h',
        title="Top States Voting Volume",
        color='total_votes',
        color_continuous_scale='Blues',
        text_auto='.2s'
    )
    fig_bar.update_layout(
        yaxis={'categoryorder': 'total ascending'}, 
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Top 10 Largest Counties by Votes")
        top_counties = filtered_df.sort_values(by='total_votes', ascending=False).head(10)
        fig_county = px.pie(
            top_counties,
            names='county',
            values='total_votes',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig_county.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig_county, use_container_width=True)

    with col_right:
        st.subheader("Reporting Progress Distribution (%)")
        fig_hist = px.histogram(
            filtered_df,
            x='percent',
            nbins=20,
            color_discrete_sequence=['#3366cc']
        )
        fig_hist.update_layout(
            xaxis_title="Reporting Percent",
            yaxis_title="County Count",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig_hist, use_container_width=True)

with tab2:
    st.subheader("Dataset Explorer")
    
    search_county = st.text_input("Search County Name:")
    display_df = filtered_df.copy()
    
    if search_county:
        display_df = display_df[display_df['county'].str.contains(search_county, case=False, na=False)]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Download Button
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name='filtered_election_data.csv',
        mime='text/csv',
    )

with tab3:
    st.subheader("Correlation & Summary Statistics")
    
    st.markdown("##### Summary Metrics")
    st.dataframe(filtered_df.describe().T, use_container_width=True)
    
    st.markdown("##### Feature Correlation Heatmap")
    numeric_df = filtered_df.select_dtypes(include=['float64', 'int64'])
    corr = numeric_df.corr()
    
    fig_corr = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale='Viridis',
        aspect="auto"
    )
    fig_corr.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
    st.plotly_chart(fig_corr, use_container_width=True)