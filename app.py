import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. Page Configuration (Must be first)
st.set_page_config(page_title="Protthapan Inventory", layout="wide", initial_sidebar_state="collapsed")

# 2. TOP HEADER & INSTANT THEME TOGGLE
# We render the header first so we can grab the toggle state instantly, eliminating the 1-click lag.
head_col1, head_col2, head_col3 = st.columns([1, 6, 2])

with head_col1:
    st.image("https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/logo.jpg", width=70)
    
with head_col2:
    st.markdown("<h1 style='margin: 0; padding: 0; font-size: 32px;'>Protthapan Technologies</h1>", unsafe_allow_html=True)
    st.markdown("<p style='margin: 0; padding: 0; font-size: 16px; opacity: 0.7; font-weight: 600;'>Inventory Management System</p>", unsafe_allow_html=True)

with head_col3:
    # Read the toggle state instantly
    is_dark = st.toggle("🌙 Dark Mode", value=False, key="theme_toggle")
    
    # 7-Segment Clock
    clock_led = "#ff3333" if is_dark else "#d32f2f"
    clock_html = f"""
    <link href="https://cdn.jsdelivr.net/npm/dseg@0.46.0/css/dseg.css" rel="stylesheet">
    <div style="text-align: right; font-family: sans-serif; margin-top: 10px;">
        <div id="clock_time" style="font-family: 'DSEG7 Classic', monospace; font-size: 24px; font-style: italic; color: {clock_led}; margin-bottom: 2px;"></div>
        <div id="clock_date" style="font-size: 13px; font-weight: bold; letter-spacing: 0.5px;"></div>
        <div id="clock_day" style="font-size: 13px; opacity: 0.8;"></div>
    </div>
    <script>
        function updateTime() {{
            const now = new Date();
            let h = String(now.getHours()).padStart(2, '0');
            let m = String(now.getMinutes()).padStart(2, '0');
            let s = String(now.getSeconds()).padStart(2, '0');
            document.getElementById('clock_time').innerText = h + ':' + m + ':' + s;
            document.getElementById('clock_date').innerText = now.toLocaleDateString('en-GB', {{ day: 'numeric', month: 'long', year: 'numeric' }});
            document.getElementById('clock_day').innerText = now.toLocaleDateString('en-GB', {{ weekday: 'long' }});
        }}
        setInterval(updateTime, 1000);
        updateTime();
    </script>
    """
    components.html(clock_html, height=85)

st.markdown("<hr style='margin-top: 5px; margin-bottom: 20px;'>", unsafe_allow_html=True)

# 3. SMART THEME ENGINE (Applies instantly based on the toggle above)
if is_dark:
    bg_color = "#121212"       
    card_bg = "#1E1E1E"        
    text_color = "#FFFFFF"     
    border_color = "#333333"   
    table_border = "#444444"
else:
    bg_color = "#F4F6F9"       
    card_bg = "#FFFFFF"        
    text_color = "#111111"     
    border_color = "#E2E8F0"   
    table_border = "#EEEEEE"

# 4. STRICT CSS INJECTION
css = f"""
<style>
    /* Global Colors */
    .stApp {{ background-color: {bg_color}; }}
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, label, .stText, th, td {{
        color: {text_color} !important;
    }}
    
    /* Clean UI Elements */
    header {{ visibility: hidden; }}
    [data-testid="stSidebar"] {{ background-color: {card_bg} !important; border-right: 1px solid {border_color}; }}
    
    /* STRICT MODAL OVERRIDE (Fixes the black/white contrast issue) */
    div[data-testid="stDialog"] > div {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
    }}
    div[data-testid="stDialog"] * {{ color: {text_color} !important; }}
    
    /* PRODUCT CARDS */
    div[data-testid="column"] {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 10px;
        position: relative; /* Anchor for the 'i' button */
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    
    /* 'i' BUTTON INSIDE THE IMAGE */
    div[data-testid="column"] .stButton {{
        position: absolute;
        top: 15px;    /* Sits inside the image frame */
        right: 15px;  /* Sits inside the image frame */
        z-index: 99;
    }}
    div[data-testid="column"] .stButton > button {{
        border-radius: 50%;
        width: 30px;
        height: 30px;
        padding: 0;
        font-weight: 800;
        background-color: rgba(255, 255, 255, 0.9) !important; /* Always light so it pops over dark images */
        color: #000000 !important; /* Always black text */
        border: 1px solid #aaa;
        box-shadow: 0 2px 5px rgba(0,0,0,0.4);
    }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 5. DATA FETCHING
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSPubWzU-KvqZFCgU_dGHxmGQxbg234qSR62w4TvyzrCPlxw1zzVsgYpbgsNYQCtw/pub?output=xlsx"

@st.cache_data(ttl=10)
def load_data():
    try:
        data = pd.read_excel(SHEET_URL, engine='openpyxl')
        data.columns = data.columns.str.strip()
        return data
    except Exception:
        return None

df = load_data()

if df is not None:
    # ---------------------------------------------------------
    # SIDEBAR CONTROLS
    # ---------------------------------------------------------
    st.sidebar.subheader("Menu Controls")
    sort_option = st.sidebar.radio("Sort Inventory:", ["Default", "A to Z", "Z to A", "Price: High to Low", "Price: Low to High"])
    
    cat_list = list(df['Category'].dropna().unique())
    selected_cats = st.sidebar.multiselect("Filter Category:", cat_list, default=cat_list)
    
    max_cost = float(df['Cost'].max()) if not df.empty else 100000.0
    price_limit = st.sidebar.slider("Max Price (INR):", min_value=0.0, max_value=max_cost, value=max_cost)
    show_out_of_stock = st.sidebar.checkbox("Show Out of Stock only")

    # Apply Filters
    f_df = df.copy()
    f_df = f_df[f_df['Category'].isin(selected_cats)]
    f_df = f_df[f_df['Cost'] <= price_limit]
    if show_out_of_stock:
        f_df = f_df[f_df['Physical Count'] <= 0]
        
    if sort_option == "A to Z": f_df = f_df.sort_values("Item Name", ascending=True)
    elif sort_option == "Z to A": f_df = f_df.sort_values("Item Name", ascending=False)
    elif sort_option == "Price: High to Low": f_df = f_df.sort_values("Cost", ascending=False)
    elif sort_option == "Price: Low to High": f_df = f_df.sort_values("Cost", ascending=True)

    # ---------------------------------------------------------
    # MODAL: PROFESSIONAL DATASHEET (40% / 60%)
    # ---------------------------------------------------------
    @st.dialog("Component Datasheet", width="large")
    def show_item_details(item_data):
        m_col1, m_col2 = st.columns([4, 6]) # Exact 40/60 split
        sku_id = str(item_data['SKU (ID)'])
        image_url = f"https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/{sku_id}.jpg"
        
        with m_col1:
            st.image(image_url, use_container_width=True)
            
        with m_col2:
            st.markdown(f"<h3 style='margin-top:0;'>{item_data['Item Name']}</h3>", unsafe_allow_html=True)
            
            # Professional Uniform Table layout
            table_html = f"""
            <table style="width: 100%; border-collapse: collapse; font-size: 15px; margin-top: 10px;">
                <tr style="border-bottom: 1px solid {table_border};">
                    <td style="padding: 10px 0; font-weight: bold; width: 35%;">SKU ID</td>
                    <td style="padding: 10px 0; font-family: monospace;">{item_data['SKU (ID)']}</td>
                </tr>
                <tr style="border-bottom: 1px solid {table_border};">
                    <td style="padding: 10px 0; font-weight: bold;">Category</td>
                    <td style="padding: 10px 0;">{item_data['Category']}</td>
                </tr>
                <tr style="border-bottom: 1px solid {table_border};">
                    <td style="padding: 10px 0; font-weight: bold;">Stock Level</td>
                    <td style="padding: 10px 0; color: #007bff; font-weight: bold;">{item_data['Physical Count']} {item_data['Unit']}</td>
                </tr>
                <tr style="border-bottom: 1px solid {table_border};">
                    <td style="padding: 10px 0; font-weight: bold;">Unit Cost</td>
                    <td style="padding: 10px 0;">₹ {item_data['Cost']}</td>
                </tr>
                <tr style="border-bottom: 1px solid {table_border};">
                    <td style="padding: 10px 0; font-weight: bold;">Location</td>
                    <td style="padding: 10px 0;">{item_data['Location']}</td>
                </tr>
                <tr style="border-bottom: 1px solid {table_border};">
                    <td style="padding: 10px 0; font-weight: bold;">Specifications</td>
                    <td style="padding: 10px 0;">{item_data['Specifications']}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; font-weight: bold; vertical-align: top;">Description</td>
                    <td style="padding: 10px 0; opacity: 0.9;">{item_data['Description']}</td>
                </tr>
            </table>
            """
            st.markdown(table_html, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # MAIN GRID RENDERING
    # ---------------------------------------------------------
    rows = [f_df.iloc[i:i + 4] for i in range(0, len(f_df), 4)]

    for row in rows:
        cols = st.columns(4)
        for index, (df_index, item) in enumerate(row.iterrows()):
            with cols[index]:
                sku = str(item['SKU (ID)'])
                img_url = f"https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/{sku}.jpg"
                
                # Button renders first so CSS absolute positioning places it over the image
                if st.button("i", key=f"info_{sku}"):
                    show_item_details(item)
                    
                st.image(img_url, use_container_width=True)
                st.markdown(f"<div style='text-align: center; font-weight: 600; padding-top: 8px;'>{item['Item Name']}</div>", unsafe_allow_html=True)

else:
    st.error("Data Load Failed: Check your Google Sheets link.")
