import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import requests

# 1. Page Configuration
st.set_page_config(page_title="Protthapan Inventory", layout="wide", initial_sidebar_state="collapsed")

# 2. TOP HEADER & THEME TOGGLE
head_col1, head_col2, head_col3 = st.columns([1, 6, 2])
with head_col1:
    st.image("https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/logo.jpg", width=70)
with head_col2:
    st.markdown("<h1 style='margin: 0; padding: 0; font-size: 32px;'>Protthapan Technologies</h1>", unsafe_allow_html=True)
    st.markdown("<p style='margin: 0; padding: 0; font-size: 16px; opacity: 0.7; font-weight: 600;'>Inventory Management System</p>", unsafe_allow_html=True)

with head_col3:
    is_dark = st.toggle("🌙 Dark Mode", value=False, key="theme_toggle")
    clock_led = "#ffffff" if is_dark else "#000000"
    clock_html = f"""
    <link href="https://cdn.jsdelivr.net/npm/dseg@0.46.0/css/dseg.css" rel="stylesheet">
    <div style="text-align: right; font-family: sans-serif; margin-top: 10px; color: {clock_led};">
        <div id="clock_time" style="font-family: 'DSEG7 Classic', monospace; font-size: 24px; font-style: italic;"></div>
        <div id="clock_date" style="font-size: 13px; font-weight: bold;"></div>
    </div>
    <script>
        function updateTime() {{
            const now = new Date();
            document.getElementById('clock_time').innerText = String(now.getHours()).padStart(2, '0') + ':' + String(now.getMinutes()).padStart(2, '0') + ':' + String(now.getSeconds()).padStart(2, '0');
            document.getElementById('clock_date').innerText = now.toLocaleDateString('en-GB', {{ day: 'numeric', month: 'long', year: 'numeric' }}) + ' ' + now.toLocaleDateString('en-GB', {{ weekday: 'long' }});
        }}
        setInterval(updateTime, 1000); updateTime();
    </script>"""
    components.html(clock_html, height=85)

# 3. HOME PAGE THEME & CSS
bg_color, card_bg, main_text, card_border = ("#121212", "#1E1E1E", "#FFFFFF", "#FFFFFF") if is_dark else ("#F4F6F9", "#FFFFFF", "#000000", "#000000")

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; }}
    p, h1, h2, h3, span, label, div[data-testid="stMarkdownContainer"] * {{ color: {main_text} !important; }}
    div[data-testid="column"] {{ background-color: {card_bg}; border: 2px solid {card_border} !important; border-radius: 8px; padding: 12px; }}
    div[data-testid="stDialog"] > div {{ background-color: #1A1A1A !important; border: 1px solid #444444 !important; }}
    div[data-testid="stDialog"] * {{ color: #FFFFFF !important; }}
    .stButton > button {{ background: transparent !important; color: {main_text} !important; border: none !important; font-size: 22px !important; width: 100%; display: flex; justify-content: flex-end; box-shadow: none !important; }}
</style>
""", unsafe_allow_html=True)

# 4. DATA FETCHING
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSPubWzU-KvqZFCgU_dGHxmGQxbg234qSR62w4TvyzrCPlxw1zzVsgYpbgsNYQCtw/pub?output=xlsx"

@st.cache_data(ttl=10)
def load_data():
    try:
        data = pd.read_excel(SHEET_URL, engine='openpyxl')
        data.columns = data.columns.str.strip()
        return data
    except: return None

# HELPER: Check which image exists
def get_valid_image(sku):
    base_url = "https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/"
    # Try SKU.jpg first (your current single images)
    url_v1 = f"{base_url}{sku}.jpg"
    # Try SKU_1.jpg as fallback
    url_v2 = f"{base_url}{sku}_1.jpg"
    
    # We use a HEAD request to check if the file exists without downloading it
    try:
        if requests.head(url_v1).status_code == 200: return url_v1
        return url_v2
    except: return url_v1

df = load_data()

if df is not None:
    # 5. SIDEBAR FILTERS
    st.sidebar.subheader("Menu Controls")
    sort_option = st.sidebar.radio("Sort:", ["Default", "A to Z", "Price: High to Low", "Price: Low to High"])
    cat_list = list(df['Category'].dropna().unique())
    selected_cats = st.sidebar.multiselect("Filter Category:", cat_list, default=cat_list)
    
    f_df = df[df['Category'].isin(selected_cats)].copy()
    if sort_option == "A to Z": f_df = f_df.sort_values("Item Name")
    elif sort_option == "Price: High to Low": f_df = f_df.sort_values("Cost", ascending=False)
    elif sort_option == "Price: Low to High": f_df = f_df.sort_values("Cost")

    # 6. MODAL DIALOG
    @st.dialog("Component Datasheet", width="large")
    def show_item_details(item_data):
        m_col1, m_col2 = st.columns([4, 6])
        sku = str(item_data['SKU (ID)'])
        try: img_count = int(item_data.get('Image Count', 1))
        except: img_count = 1

        with m_col1:
            if img_count <= 1:
                st.image(get_valid_image(sku), use_container_width=True)
            else:
                img_tags = ""
                for i in range(1, img_count + 1):
                    display = "block" if i == 1 else "none"
                    url = f"https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/{sku}_{i}.jpg"
                    img_tags += f'<img class="slide" src="{url}" style="max-width:100%; display:{display}; margin:auto; border-radius:8px;">'
                
                slider_html = f"""
                <div id="s" style="position:relative; height:320px; display:flex; align-items:center; justify-content:center;">
                    <button onclick="m(-1)" style="position:absolute; left:5px; z-index:10; cursor:pointer;">&#10094;</button>
                    {img_tags}
                    <button onclick="m(1)" style="position:absolute; right:5px; z-index:10; cursor:pointer;">&#10095;</button>
                </div>
                <script>
                    let idx = 0; const slides = document.querySelectorAll('.slide');
                    function m(d) {{ slides[idx].style.display='none'; idx=(idx+d+slides.length)%slides.length; slides[idx].style.display='block'; }}
                </script>"""
                components.html(slider_html, height=330)

        with m_col2:
            st.markdown(f"### {item_data['Item Name']}")
            st.write(f"**SKU:** `{sku}`")
            st.write(f"**Stock:** {item_data['Physical Count']} {item_data['Unit']}")
            st.write(f"**Cost:** ₹{item_data['Cost']}")
            st.write(f"**Location:** {item_data['Location']}")
            st.write(f"**Specs:** {item_data['Specifications']}")
            st.write(f"**Description:** {item_data['Description']}")

    # 7. MAIN GRID
    for i in range(0, len(f_df), 4):
        cols = st.columns(4)
        for j, (idx, item) in enumerate(f_df.iloc[i:i+4].iterrows()):
            with cols[j]:
                sku = str(item['SKU (ID)'])
                st.image(get_valid_image(sku), use_container_width=True)
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{item['Item Name']}**")
                if c2.button("ⓘ", key=f"btn_{sku}"): show_item_details(item)
