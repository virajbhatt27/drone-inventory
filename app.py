import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(page_title="Protthapan Inventory", layout="wide")

# 2. Theme State Management
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# 3. Sidebar (Opens/Closes via 3-line menu)
st.sidebar.title("Settings & Controls")
st.session_state.dark_mode = st.sidebar.toggle("Enable Dark Mode", st.session_state.dark_mode)

# Define Smart Colors based on Theme
if st.session_state.dark_mode:
    bg_color = "#121212"       # Deep Charcoal
    card_bg = "#1E1E1E"        # Slightly lighter charcoal for contrast
    text_color = "#F0F0F0"     # Soft White
    border_color = "#333333"   # Dark border
else:
    bg_color = "#F4F6F9"       # Soft Pearl Grey
    card_bg = "#FFFFFF"        # Pure White
    text_color = "#1A1A1A"     # Crisp Black
    border_color = "#E2E8F0"   # Light border

# 4. Inject Dynamic CSS (Handles Text Colors, Card UI, and 'i' Button placement)
css = f"""
<style>
    /* Main Background */
    .stApp {{ background-color: {bg_color}; }}
    
    /* Force Text Color for Readability */
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6, label, .stText {{
        color: {text_color} !important;
    }}
    
    /* Clean up default Streamlit UI */
    header {{ visibility: hidden; }}
    
    /* Style the Sidebar */
    [data-testid="stSidebar"] {{ background-color: {card_bg} !important; border-right: 1px solid {border_color}; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{ color: {text_color} !important; }}
    
    /* Style the 4-Column Product Cards */
    div[data-testid="column"] {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        position: relative; /* Required to pin the 'i' button */
        min-height: 280px;
    }}
    
    /* Make the 'i' button circular and place it in the bottom right */
    div[data-testid="column"] .stButton > button {{
        border-radius: 50%;
        width: 32px;
        height: 32px;
        padding: 0;
        font-weight: bold;
        position: absolute;
        bottom: 15px;
        right: 15px;
        background-color: {bg_color};
        color: {text_color};
        border: 1px solid {border_color};
        transition: 0.3s;
    }}
    div[data-testid="column"] .stButton > button:hover {{
        border-color: #007BFF;
        color: #007BFF;
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
    # SIDEBAR: SORTING & FILTERING
    # ---------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.subheader("Sort")
    sort_option = st.sidebar.radio("Order items by:", ["Default", "A to Z", "Z to A", "Price: High to Low", "Price: Low to High"])
    
    st.sidebar.subheader("Filter")
    cat_list = list(df['Category'].dropna().unique())
    selected_cats = st.sidebar.multiselect("Show Specific Categories:", cat_list, default=cat_list)
    
    max_cost = float(df['Cost'].max()) if not df.empty else 100000.0
    price_limit = st.sidebar.slider("Show items below (INR):", min_value=0.0, max_value=max_cost, value=max_cost)
    
    show_out_of_stock = st.sidebar.checkbox("Only show Out of Stock items")

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
    # HEADER: LOGO, TITLE, AND FASHIONABLE CLOCK
    # ---------------------------------------------------------
    head_col1, head_col2, head_col3 = st.columns([1, 5, 3])
    
    with head_col1:
        st.image("https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/logo.jpg", width=80)
        
    with head_col2:
        st.markdown(f"<h1 style='margin: 0; padding: 0; color: {text_color};'>Protthapan Technologies</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='margin: 0; padding: 0; font-size: 18px; font-weight: bold; color: {text_color}; opacity: 0.7;'>Inventory</p>", unsafe_allow_html=True)
        
    with head_col3:
        # Sleek, modern clock that matches the active theme
        clock_html = f"""
        <div style="background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 8px; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; color: {text_color}; font-family: sans-serif;">
            <div>
                <div id="clock_date" style="font-size: 14px; font-weight: bold; letter-spacing: 0.5px;"></div>
                <div id="clock_day" style="font-size: 12px; opacity: 0.8; margin-top: 2px;"></div>
            </div>
            <div id="clock_time" style="font-size: 24px; font-weight: 700; font-family: monospace; letter-spacing: 1px;"></div>
        </div>
        <script>
            function updateTime() {{
                const now = new Date();
                document.getElementById('clock_date').innerText = now.toLocaleDateString('en-GB', {{ day: 'numeric', month: 'long', year: 'numeric' }});
                document.getElementById('clock_time').innerText = now.toLocaleTimeString('en-GB', {{ hour12: false }});
                document.getElementById('clock_day').innerText = now.toLocaleDateString('en-GB', {{ weekday: 'long' }});
            }}
            setInterval(updateTime, 1000);
            updateTime();
        </script>
        """
        components.html(clock_html, height=80)

    st.markdown("<hr style='margin-top: 5px; margin-bottom: 20px;'>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # POP-UP DIALOG (Shows full details when 'i' is clicked)
    # ---------------------------------------------------------
    @st.dialog("Item Specifications", width="large")
    def show_item_details(item_data):
        m_col1, m_col2 = st.columns([1, 1.5])
        sku_id = str(item_data['SKU (ID)'])
        image_url = f"https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/{sku_id}.jpg"
        
        with m_col1:
            st.image(image_url, use_container_width=True)
            
        with m_col2:
            st.subheader(item_data['Item Name'])
            # Formatted in a single line as requested
            st.write(f"**Count:** {item_data['Physical Count']} {item_data['Unit']} | **Cost:** INR {item_data['Cost']}")
            st.markdown("---")
            st.write(f"**Specifications:** {item_data['Specifications']}")
            st.write(f"**Description:** {item_data['Description']}")
            st.write(f"**Location:** {item_data['Location']}")

    # ---------------------------------------------------------
    # MAIN GRID (Max 4 products per line)
    # ---------------------------------------------------------
    rows = [f_df.iloc[i:i + 4] for i in range(0, len(f_df), 4)]

    for row in rows:
        cols = st.columns(4)
        for index, (df_index, item) in enumerate(row.iterrows()):
            with cols[index]:
                sku = str(item['SKU (ID)'])
                img_url = f"https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/{sku}.jpg"
                
                st.image(img_url, use_container_width=True)
                st.write(f"**{item['Item Name']}**")
                
                # The functional 'i' button
                if st.button("i", key=f"info_{sku}"):
                    show_item_details(item)
else:
    st.error("Unable to load data. Please check the Google Sheet link.")
