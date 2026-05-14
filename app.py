import streamlit as st
import pandas as pd
import json
import os

# 1. Page Config
st.set_page_config(page_title="Rate-The-Star", layout="wide")

# 2. Header
st.title("🌟 Rate-The-Star Dashboard")
st.markdown("Welcome to the live interface for your Media Accountability Tracker.")

# 3. Robust Data Loader
def load_data():
    if not os.path.exists("news_data.json"):
        return pd.DataFrame()
    try:
        with open("news_data.json", "r") as file:
            data = json.load(file)
            if not data:
                return pd.DataFrame()
            
            df = pd.DataFrame(data)
            
            # Data Cleaning: Fix missing dates for older entries
            if 'date' not in df.columns:
                df['date'] = "Historical Data"
            
            # Ensure rating is a number so the chart works
            df['rating_code'] = pd.to_numeric(df['rating_code'], errors='coerce')
            return df
    except Exception:
        return pd.DataFrame()

# 4. Run the Loader
df = load_data()

# 5. Display Content
if df.empty:
    st.info("The database is currently empty. Go back to your terminal and log a new news report to see it appear here!")
else:
    # Sidebar search/filter
    st.sidebar.header("Filter Options")
    platform_search = st.sidebar.text_input("Search for a Platform (e.g. Hindu, Bhaskar)")
    
    display_df = df
    if platform_search:
        display_df = df[df['platform'].str.contains(platform_search, case=False)]

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📰 Recent Reports")
        st.dataframe(display_df[['date', 'reporter', 'platform', 'rating_code']], width="stretch")

    with col2:
        st.subheader("📊 Credibility Stats")
        avg_ratings = df.groupby('platform')['rating_code'].mean().sort_values()
        st.bar_chart(avg_ratings)