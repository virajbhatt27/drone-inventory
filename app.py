import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# This will refresh the entire app every 30 seconds automatically
# 30000 milliseconds = 30 seconds
st_autorefresh(interval=30000, key="datarefresh")
# 1. Professional UI Setup
st.set_page_config(page_title="DroneFlow Pro", layout="wide", page_icon="🚁")

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    div[data-testid="stMetric"] { background: white; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# 2. THE LINK (Replace with your Published Link from Step 1)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSPubWzU-KvqZFCgU_dGHxmGQxbg234qSR62w4TvyzrCPlxw1zzVsgYpbgsNYQCtw/pub?output=xlsx"

@st.cache_data(ttl=10) # Auto-refreshes every 10 seconds
def load_data():
    return pd.read_excel(SHEET_URL, engine='openpyxl')

try:
    df = load_data()
    df.columns = df.columns.str.strip()

    st.title("🚁 Drone Manufacturing Inventory")
    
    # --- SIDEBAR CONTROLS (Sorting & Filtering) ---
    st.sidebar.header("🛠 Controls")
    search = st.sidebar.text_input("🔍 Search Item or SKU")
    
    # Category Filter
    all_cats = ["All"] + list(df['Category'].unique())
    selected_cat = st.sidebar.selectbox("📂 Category", all_cats)
    
    # Sorting
    sort_by = st.sidebar.radio("🔃 Sort By", ["Stock: Low to High", "Cost: High to Low", "Alphabetical"])

    # --- FILTER LOGIC ---
    f_df = df.copy()
    if search:
        f_df = f_df[f_df['Item Name'].str.contains(search, case=False, na=False) | f_df['SKU (ID)'].str.contains(search, case=False, na=False)]
    if selected_cat != "All":
        f_df = f_df[f_df['Category'] == selected_cat]
    
    if sort_by == "Stock: Low to High":
        f_df = f_df.sort_values("Physical Count")
    elif sort_by == "Cost: High to Low":
        f_df = f_df.sort_values("Cost", ascending=False)
    else:
        f_df = f_df.sort_values("Item Name")

    # --- TOP METRICS ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Items", int(f_df['Physical Count'].sum()))
    c2.metric("Inventory Value", f"₹{(f_df['Physical Count'] * f_df['Cost']).sum():,.0f}")
    c3.metric("Low Stock Alerts", len(f_df[f_df['Physical Count'] < 5]))

    # --- GRID DISPLAY ---
    for _, row in f_df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            sku = str(row['SKU (ID)'])
            
            with col1:
                # Direct link to your GitHub assets
                img_url = f"https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/{sku}.jpg"
                st.image(img_url, use_container_width=True, caption=sku)
            
            with col2:
                st.subheader(row['Item Name'])
                st.write(f"**Loc:** {row['Location']} | **Spec:** {row['Specifications']}")
                st.caption(row['Description'])
            
            with col3:
                count = int(row['Physical Count'])
                if count < 5:
                    st.error(f"Stock: {count}")
                else:
                    st.success(f"Stock: {count}")
                st.write(f"**Unit Cost:** ₹{row['Cost']}")
            st.divider()

except Exception as e:
    st.error(f"Live Sync Error: {e}")
    st.info("Check your Google Sheet 'Publish to Web' link.")
