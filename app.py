import streamlit as st
import pandas as pd
import os

# 1. Config
st.set_page_config(page_title="DroneFlow Pro", layout="wide", page_icon="🛸")

# 2. Load Data 
@st.cache_data
def load_data():
    try:
        data = pd.read_excel("inventory.xlsx")
        data.columns = data.columns.str.strip() # Clean headers
        return data
    except Exception as e:
        st.error(f"Excel Error: {e}")
        return None

df = load_data()

if df is not None:
    st.title("🚁 Drone Manufacturing Inventory")
    
    # Sidebar Filters
    search = st.sidebar.text_input("🔍 Search Item or SKU")
    
    display_df = df.copy()
    if search:
        display_df = display_df[
            display_df['Item Name'].astype(str).str.contains(search, case=False) | 
            display_df['SKU (ID)'].astype(str).str.contains(search, case=False)
        ]

    # Grid Display
    for index, row in display_df.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([1, 2, 1])
            
            # Look for SKU.jpg or SKU.png
            sku = str(row['SKU (ID)'])
            img_path = f"assets/{sku}.jpg"
            
            with c1:
                if os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/200?text=No+Photo", use_container_width=True)
            
            with c2:
                st.subheader(row['Item Name'])
                st.caption(f"SKU: {sku} | Location: {row['Location']}")
                st.write(f"**Specs:** {row['Specifications']}")
            
            with c3:
                st.metric("In Stock", f"{row['Physical Count']} {row['Unit']}")
                st.write(f"**Cost:** ₹{row['Cost']}")
            st.divider()
