import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(page_title="Protthapan Inventory", layout="wide", initial_sidebar_state="collapsed")

# 2. TOP HEADER & INSTANT THEME TOGGLE
head_col1, head_col2, head_col3 = st.columns([1, 6, 2])

with head_col1:
    st.image("https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/logo.jpg", width=70)
    
with head_col2:
    st.markdown("<h1 style='margin: 0; padding: 0; font-size: 32px;'>Protthapan Technologies</h1>", unsafe_allow_html=True)
    st.markdown("<p style='margin: 0; padding: 0; font-size: 16px; opacity: 0.7; font-weight: 600;'>Inventory Management System</p>", unsafe_allow_html=True)

with head_col3:
    is_dark = st.toggle("🌙 Dark Mode", value=False, key="theme_toggle")
    
    clock_led = "#ffffff" if is_dark else "#000000"
    clock_text = "#ffffff" if is_dark else "#000000"
    
    clock_html = f"""
    <link href="https://cdn.jsdelivr.net/npm/dseg@0.46.0/css/dseg.css" rel="stylesheet">
    <div style="text-align: right; font-family: sans-serif; margin-top: 10px; color: {clock_text};">
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

# 3. STRICT INVERTED THEME ENGINE
if is_dark:
    # Home Page: DARK
    bg_color = "#121212"       
    card_bg = "#1E1E1E"        
    main_text = "#FFFFFF"      
    card_border = "#FFFFFF"    
    border_color = "#333333"   
    
    # Modal Pop-up: LIGHT (Inverted)
    modal_bg = "#F4F6F9"
    modal_text = "#000000"     
    modal_border = "#CCCCCC"
    table_border = "#DDDDDD"
else:
    # Home Page: LIGHT
    bg_color = "#F4F6F9"       
    card_bg = "#FFFFFF"        
    main_text = "#000000"      
    card_border = "#000000"    
    border_color = "#E2E8F0"   
    
    # Modal Pop-up: DARK (Inverted)
    modal_bg = "#1A1A1A"
    modal_text = "#FFFFFF"     
    modal_border = "#444444"
    table_border = "#333333"

# 4. CSS INJECTION (Strict Class Targeting)
css = f"""
<style>
    /* 1. Global Home Page Settings */
    .stApp {{ background-color: {bg_color}; }}
    
    p, h1, h2, h3, h4, span, label, div[data-testid="stMarkdownContainer"] * {{
        color: {main_text} !important;
    }}
    
    /* FIX: Restore the 3-line menu but hide Streamlit watermarks */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header {{ background-color: transparent !important; }}
    
    [data-testid="stSidebar"] {{ background-color: {card_bg} !important; border-right: 1px solid {border_color}; }}
    
    /* 2. PRODUCT CARDS */
    div[data-testid="column"] {{
        background-color: {card_bg};
        border: 2px solid {card_border} !important; 
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    /* 3. 'ⓘ' BUTTON ICON STYLING (Completely Transparent Background) */
    div[data-testid="column"] .stButton > button,
    div[data-testid="column"] .stButton > button:hover,
    div[data-testid="column"] .stButton > button:focus,
    div[data-testid="column"] .stButton > button:active {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        color: {main_text} !important; 
        font-size: 22px !important;
        padding: 0;
        height: auto;
        width: 100%;
        display: flex;
        justify-content: flex-end;
        box-shadow: none !important;
    }}
    div[data-testid="column"] .stButton > button:hover {{
        opacity: 0.6;
    }}

    /* 4. STRICT INVERTED MODAL (POP-UP) RULES */
    div[data-testid="stDialog"] > div {{
        background-color: {modal_bg} !important;
        border: 1px solid {modal_border} !important;
    }}
    
    div[data-testid="stDialog"] p,
    div[data-testid="stDialog"] h1,
    div[data-testid="stDialog"] h2,
    div[data-testid="stDialog"] h3,
    div[data-testid="stDialog"] span,
    div[data-testid="stDialog"] td,
    div[data-testid="stDialog"] th,
    div[data-testid="stDialog"] div {{
        color: {modal_text} !important;
    }}
    
    div[data-testid="stDialog"] svg {{
        fill: {modal_text} !important;
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
        m_col1, m_col2 = st.columns([4, 6]) 
        sku_id = str(item_data['SKU (ID)'])
        image_url = f"https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/{sku_id}.jpg"
        
        with m_col1:
            st.image(image_url, use_container_width=True)
            
        with m_col2:
            st.markdown(f"<h3 style='margin-top:0;'>{item_data['Item Name']}</h3>", unsafe_allow_html=True)
            
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
                    <td style="padding: 10px 0; font-weight: bold;">{item_data['Physical Count']} {item_data['Unit']}</td>
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
                
                st.image(img_url, use_container_width=True)
                
                name_col, btn_col = st.columns([5, 1])
                
                with name_col:
                    st.markdown(f"<div style='font-weight: 600; padding-top: 5px; font-size: 15px;'>{item['Item Name']}</div>", unsafe_allow_html=True)
                
                with btn_col:
                    if st.button("ⓘ", key=f"info_{sku}"):
                        show_item_details(item)

else:
    st.error("Data Load Failed: Check your Google Sheets link.")
