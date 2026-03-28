import streamlit as st
import pandas as pd

# 1. Page Configuration for a Premium Look
st.set_page_config(page_title="DroneFlow Pro", layout="wide", page_icon="🚁")

# Custom CSS for a clean, modern interface
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stMetricValue"] { color: #1f77b4; }
    </style>
    """, unsafe_allow_html=True)

# 2. THE LIVE LINK (CRITICAL)
# Go to Google Sheets > File > Share > Publish to Web > Select XLSX > Copy that link here!
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSPubWzU-KvqZFCgU_dGHxmGQxbg234qSR62w4TvyzrCPlxw1zzVsgYpbgsNYQCtw/pubhtml"

@st.cache_data(ttl=10) # Refreshes every 10 seconds automatically
def load_live_data():
    return pd.read_excel(SHEET_URL)

try:
    df = load_live_data()
    df.columns = df.columns.str.strip() # Clean headers

    # --- UI HEADER ---
    st.title("🚁 Drone Manufacturing Inventory")
    st.caption("Live Cloud Sync Active • Updated every 10 seconds")
    
    # --- DASHBOARD METRICS ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total SKUs", len(df))
    col2.metric("Total Items", int(df['Physical Count'].sum()))
    col3.metric("Stock Value", f"₹{(df['Physical Count'] * df['Cost']).sum():,.0f}")
    col4.metric("Low Stock", len(df[df['Physical Count'] < 5]))
    
    st.divider()

    # --- POWERFUL FILTERS (SIDEBAR) ---
    st.sidebar.header("🛠 Controls")
    search = st.sidebar.text_input("🔍 Search Item or SKU")
    
    # Category Filter
    all_cats = ["All"] + list(df['Category'].unique())
    selected_cat = st.sidebar.selectbox("📂 Filter by Category", all_cats)
    
    # Sorting Filter
    sort_option = st.sidebar.radio("🔃 Sort By", ["Recent (Date)", "Stock: Low to High", "Cost: High to Low"])

    # --- FILTER LOGIC ---
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df['Item Name'].str.contains(search, case=False) | filtered_df['SKU (ID)'].str.contains(search, case=False)]
    if selected_cat != "All":
        filtered_df = filtered_df[filtered_df['Category'] == selected_cat]
    
    if sort_option == "Stock: Low to High":
        filtered_df = filtered_df.sort_values("Physical Count")
    elif sort_option == "Cost: High to Low":
        filtered_df = filtered_df.sort_values("Cost", ascending=False)
    else:
        filtered_df = filtered_df.sort_values("Date", ascending=False)

    # --- THE DISPLAY GRID ---
    for _, row in filtered_df.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([1, 2, 1])
            
            with c1:
                # Still using GitHub for photos as it's the fastest free way
                sku = str(row['SKU (ID)'])
                img_url = f"https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/{sku}.jpg"
                st.image(img_url, use_container_width=True)
            
            with c2:
                st.subheader(row['Item Name'])
                st.write(f"**Category:** {row['Category']} | **Loc:** {row['Location']}")
                st.write(f"*{row['Description']}*")
                st.caption(f"Spec: {row['Specifications']}")
            
            with c3:
                # Color code stock levels
                stock = int(row['Physical Count'])
                if stock < 5:
                    st.error(f"⚠️ LOW STOCK: {stock}")
                else:
                    st.success(f"✅ In Stock: {stock}")
                st.write(f"**Unit Cost:** ₹{row['Cost']}")
            
            st.divider()

except Exception as e:
    st.error(f"Live Sync Error: {e}")
    st.info("Ensure your Google Sheet is 'Published to Web' as an XLSX file.")