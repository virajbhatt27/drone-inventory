import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(page_title="DroneFlow Inventory", layout="wide", page_icon="🛸")

# Custom CSS for a "Premium" look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .item-card { border: 1px solid #e6e9ef; padding: 15px; border-radius: 10px; background: white; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Engine
@st.cache_data
def load_data():
    return pd.read_excel("inventory.xlsx")

df = load_data()

# 3. Sidebar - Advanced Filtering
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/252/252035.png", width=100)
st.sidebar.title("DroneFlow Pro")

search = st.sidebar.text_input("🔍 Search Inventory", placeholder="Type SKU or Name...")
category_filter = st.sidebar.multiselect("Category", options=df["Category"].unique())
sort_by = st.sidebar.selectbox("Sort By", ["Item Name", "Cost (High to Low)", "Physical Count (Low to High)"])

# Applying Filters
filtered_df = df.copy()
if search:
    filtered_df = filtered_df[filtered_df['Item Name'].str.contains(search, case=False) | filtered_df['SKU (ID)'].str.contains(search, case=False)]
if category_filter:
    filtered_df = filtered_df[filtered_df['Category'].isin(category_filter)]

# Sorting Logic
if sort_by == "Cost (High to Low)":
    filtered_df = filtered_df.sort_values("Cost", ascending=False)
elif sort_by == "Physical Count (Low to High)":
    filtered_df = filtered_df.sort_values("Physical Count", ascending=True)

# 4. Main Dashboard UI
st.title("🚁 Manufacturing Inventory")
col1, col2, col3 = st.columns(3)
col1.metric("SKUs Tracked", len(filtered_df))
col2.metric("Total Stock Value", f"₹{ (filtered_df['Cost'] * filtered_df['Physical Count']).sum():,.0f}")
col3.metric("Low Stock Items", len(filtered_df[filtered_df['Physical Count'] < 5]))

st.divider()

# 5. The "Photo & Details" Grid
for index, row in filtered_df.iterrows():
    with st.container():
        c1, c2, c3 = st.columns([1, 2, 1])
        
        # Image Logic
        img_path = f"assets/{row['SKU (ID)']}.jpg"
        with c1:
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            else:
                st.image("https://via.placeholder.com/150?text=No+Photo", use_container_width=True)
        
        with c2:
            st.subheader(row['Item Name'])
            st.caption(f"SKU: {row['SKU (ID)']} | Location: {row['Location']}")
            st.write(f"**Spec:** {row['Specifications']}")
            st.write(f"**Desc:** {row['Description']}")
        
        with c3:
            st.write("###")
            st.metric("In Stock", f"{row['Physical Count']} {row['Unit']}")
            st.write(f"**Unit Cost:** ₹{row['Cost']}")
        
        st.divider()