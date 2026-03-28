import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Page Config & Professional Styling
st.set_page_config(page_title="DroneFlow Gallery", layout="wide", page_icon="🛸")

# Custom CSS for a clean "Grid" look
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #f0f2f6; color: #31333F; border: 1px solid #dcdfe3; }
    .stButton>button:hover { background-color: #007bff; color: white; border: 1px solid #007bff; }
    div[data-testid="column"] { padding: 10px; border: 1px solid #f0f2f6; border-radius: 10px; background: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. Auto-Refresh every 60 seconds to stay in sync with Google Sheets
st_autorefresh(interval=60000, key="frequent_sync")

# 3. Data Engine (Replace with your actual Published Google Sheet Link)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSPubWzU-KvqZFCgU_dGHxmGQxbg234qSR62w4TvyzrCPlxw1zzVsgYpbgsNYQCtw/pub?output=xlsx"

@st.cache_data(ttl=10)
def load_live_data():
    try:
        data = pd.read_excel(SHEET_URL, engine='openpyxl')
        data.columns = data.columns.str.strip()
        return data
    except Exception as e:
        st.error(f"Sync Error: {e}")
        return None

df = load_live_data()

if df is not None:
    # --- HEADER ---
    st.title("🚁 Manufacturing Inventory Gallery")
    
    # --- SEARCH & FILTER (One line) ---
    search_col, cat_col = st.columns([2, 1])
    with search_col:
        search = st.text_input("🔍 Search by Name or SKU", placeholder="Search...")
    with cat_col:
        categories = ["All Categories"] + list(df['Category'].unique())
        selected_cat = st.selectbox("📂 Filter", categories)

    # Filtering Logic
    f_df = df.copy()
    if search:
        f_df = f_df[f_df['Item Name'].str.contains(search, case=False, na=False) | f_df['SKU (ID)'].str.contains(search, case=False, na=False)]
    if selected_cat != "All Categories":
        f_df = f_df[f_df['Category'] == selected_cat]

    st.divider()

    # --- THE 4-COLUMN GRID ---
    # We loop through the data and create a new row every 4 items
    rows = [f_df[i:i + 4] for i in range(0, len(f_df), 4)]

    for row_data in rows:
        cols = st.columns(4)
        for i, (index, item) in enumerate(row_data.iterrows()):
            with cols[i]:
                sku = str(item['SKU (ID)'])
                # Photo Link from GitHub
                img_url = f"https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/{sku}.jpg"
                
                st.image(img_url, use_container_width=True)
                st.subheader(item['Item Name'])
                
                # Simple Stock Indicator
                count = int(item['Physical Count'])
                if count < 5:
                    st.warning(f"Stock: {count}")
                else:
                    st.success(f"Stock: {count}")
                
                # THE "KNOW ALL DETAILS" BUTTON
                # We use a unique key for every button
                if st.button(f"View Details", key=f"btn_{sku}"):
                    st.info(f"**Full Specifications:**\n{item['Specifications']}")
                    st.write(f"**Description:** {item['Description']}")
                    st.write(f"**Location:** {item['Location']}")
                    st.write(f"**Unit Cost:** ₹{item['Cost']}")
                    st.write(f"**Last Audit:** {item['Date']}")

# 4. Error Message if Sheet is disconnected
else:
    st.warning("Connect your Google Sheet 'Publish to Web' link to begin.")
