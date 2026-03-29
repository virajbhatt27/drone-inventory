import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(page_title="Protthapan Inventory", layout="wide")

# 2. State Management for Theme
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# 3. Define Smart Colors based on Theme
if st.session_state.dark_mode:
    bg_color = "#121212"       # Deep Charcoal
    card_bg = "#1E1E1E"        # Slightly lighter charcoal
    text_color = "#FFFFFF"     # Pure White for Dark Mode
    border_color = "#333333"   
    clock_led = "#ff3333"      # Red LED color
else:
    bg_color = "#F4F6F9"       # Soft Pearl Grey
    card_bg = "#FFFFFF"        # Pure White
    text_color = "#000000"     # Pure Black for Light Mode
    border_color = "#E2E8F0"   
    clock_led = "#d32f2f"      # Darker Red LED for light mode

# 4. Inject Dynamic CSS (Fixes the Modal Bug and Positions the 'i' button)
css = f"""
<style>
    /* Main Background */
    .stApp {{ background-color: {bg_color}; }}
    
    /* Force Text Color Everywhere */
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, label, .stText, [data-testid="stMarkdownContainer"] * {{
        color: {text_color} !important;
    }}
    
    /* Clean up default UI */
    header {{ visibility: hidden; }}
    
    /* FIX: Force Dialog (Modal) Background and Text Colors */
    div[data-testid="stDialog"] > div {{
        background-color: {card_bg} !important;
        border: 1px solid {border_color} !important;
    }}
    
    /* Style the Sidebar */
    [data-testid="stSidebar"] {{ background-color: {card_bg} !important; border-right: 1px solid {border_color}; }}
    
    /* Style the 4-Column Product Cards */
    div[data-testid="column"] {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 12px;
        position: relative; /* Crucial for absolute positioning of 'i' button */
    }}
    
    /* Move the 'i' button to the TOP RIGHT of the IMAGE */
    div[data-testid="column"] .stButton {{
        position: absolute;
        top: 15px;
        right: 15px;
        z-index: 10;
    }}
    div[data-testid="column"] .stButton > button {{
        border-radius: 50%;
        width: 28px;
        height: 28px;
        padding: 0;
        font-weight: bold;
        background-color: rgba(255, 255, 255, 0.85) !important; /* Always light so it shows over photos */
        color: #000000 !important; /* Always black text */
        border: 1px solid #ccc;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 5. Data Engine
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSPubWzU-KvqZFCgU_dGHxmGQxbg234qSR62w4TvyzrCPlxw1zzVsgYpbgsNYQCtw/pub?output=xlsx"

@st.cache_data(ttl=10)
def load_data():
    try:
        data = pd.read_excel(SHEET_URL, engine='openpyxl')
        data.columns = data.columns.str.strip()
        return data
    except Exception as e:
        return None

df = load_data()

if df is not None:
    # ---------------------------------------------------------
    # TOP HEADER: Logo, Title, Theme Switcher & 7-Segment Clock
    # ---------------------------------------------------------
    head_col1, head_col2, head_col3 = st.columns([1, 6, 2])
    
    with head_col1:
        st.image("https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/logo.jpg", width=80)
        
    with head_col2:
        st.markdown(f"<h1 style='margin: 0; padding: 0;'>Protthapan Technologies</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='margin: 0; padding: 0; font-size: 16px; opacity: 0.8;'>Inventory</p>", unsafe_allow_html=True)
        
    with head_col3:
        # 1. The Light/Dark Mode Switcher (Top Right)
        st.session_state.dark_mode = st.toggle("🌙 Dark Mode", st.session_state.dark_mode)
        
        # 2. The 7-Segment Hardware Clock
        clock_html = f"""
        <link href="https://cdn.jsdelivr.net/npm/dseg@0.46.0/css/dseg.css" rel="stylesheet">
        <div style="text-align: right; color: {text_color}; font-family: sans-serif;">
            <div id="clock_time" style="font-family: 'DSEG7 Classic', monospace; font-size: 26px; font-style: italic; color: {clock_led}; margin-bottom: 4px;"></div>
            <div id="clock_date" style="font-size: 14px; margin-bottom: 2px;"></div>
            <div id="clock_day" style="font-size: 14px; opacity: 0.8;"></div>
        </div>
        <script>
            function updateTime() {{
                const now = new Date();
                let hours = String(now.getHours()).padStart(2, '0');
                let minutes = String(now.getMinutes()).padStart(2, '0');
                let seconds = String(now.getSeconds()).padStart(2, '0');
                
                document.getElementById('clock_time').innerText = hours + ':' + minutes + ':' + seconds;
                document.getElementById('clock_date').innerText = now.toLocaleDateString('en-GB', {{ day: 'numeric', month: 'long', year: 'numeric' }});
                document.getElementById('clock_day').innerText = now.toLocaleDateString('en-GB', {{ weekday: 'long' }});
            }}
            setInterval(updateTime, 1000);
            updateTime();
        </script>
        """
        components.html(clock_html, height=90)

    st.markdown("<hr style='margin-top: 0px; margin-bottom: 15px;'>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # SIDEBAR: Filtering & Sorting
    # ---------------------------------------------------------
    st.sidebar.subheader("Controls")
    sort_option = st.sidebar.radio("Sort By:", ["Default", "A to Z", "Z to A", "Price: High to Low", "Price: Low to High"])
    
    cat_list = list(df['Category'].dropna().unique())
    selected_cats = st.sidebar.multiselect("Filter Category:", cat_list, default=cat_list)
    
    max_cost = float(df['Cost'].max()) if not df.empty else 100000.0
    price_limit = st.sidebar.slider("Max Price (INR):", min_value=0.0, max_value=max_cost, value=max_cost)
    show_out_of_stock = st.sidebar.checkbox("Show Out of Stock only")

    # Apply Logic
    f_df = df.copy()
    f_df = f_df[f_df['Category'].isin(selected_cats)]
    f_df = f_df[f_df['Cost'] <= price_limit]
    if show_out_of_stock:
        f_df = f_df[f_df['Physical Count'] <= 0]
        
    if sort_option == "A to Z":
        f_df = f_df.sort_values("Item Name", ascending=True)
    elif sort_option == "Z to A":
        f_df = f_df.sort_values("Item Name", ascending=False)
    elif sort_option == "Price: High to Low":
        f_df = f_df.sort_values("Cost", ascending=False)
    elif sort_option == "Price: Low to High":
        f_df = f_df.sort_values("Cost", ascending=True)

    # ---------------------------------------------------------
    # MODAL: Exactly 40% Image / 60% Data
    # ---------------------------------------------------------
    @st.dialog("Inventory Details", width="large")
    def show_item_details(item_data):
        # 40% left column, 60% right column
        m_col1, m_col2 = st.columns([4, 6]) 
        sku_id = str(item_data['SKU (ID)'])
        image_url = f"https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/{sku_id}.jpg"
        
        with m_col1:
            st.image(image_url, use_container_width=True)
            
        with m_col2:
            st.subheader(item_data['Item Name'])
            st.write(f"**Stock:** {item_data['Physical Count']} {item_data['Unit']} &nbsp;|&nbsp; **Cost:** INR {item_data['Cost']}")
            st.markdown("---")
            st.write(f"**Specs:** {item_data['Specifications']}")
            st.write(f"**Details:** {item_data['Description']}")
            st.write(f"**Location:** {item_data['Location']}")
            st.caption(f"Last Audit: {item_data['Date']} | SKU: {sku_id}")

    # ---------------------------------------------------------
    # MAIN GRID
    # ---------------------------------------------------------
    rows = [f_df.iloc[i:i + 4] for i in range(0, len(f_df), 4)]

    for row in rows:
        cols = st.columns(4)
        for index, (df_index, item) in enumerate(row.iterrows()):
            with cols[index]:
                sku = str(item['SKU (ID)'])
                img_url = f"https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/{sku}.jpg"
                
                # The 'i' button is placed first so CSS can pin it over the image
                if st.button("i", key=f"info_{sku}"):
                    show_item_details(item)
                    
                st.image(img_url, use_container_width=True)
                st.write(f"{item['Item Name']}")

else:
    st.error("Unable to load data. Please check the Google Sheet link.")
