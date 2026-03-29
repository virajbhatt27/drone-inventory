import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(page_title="Protthapan Inventory", layout="wide")

# 2. Custom CSS Theme (Light Pink/Grey, Plain, No Emojis)
st.markdown("""
    <style>
    /* Light pastel background */
    .stApp { background-color: #faf5f7; }
    
    /* Clean up default Streamlit UI elements */
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Clean Card Styling for Products */
    div[data-testid="column"] { 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 8px; 
        border: 1px solid #eaeaeb; 
    }
    
    /* Make the 'i' button circular and small */
    .stButton>button {
        border-radius: 50%;
        width: 35px;
        height: 35px;
        padding: 0;
        font-weight: bold;
        color: #555;
        border: 1px solid #ccc;
        background: white;
    }
    .stButton>button:hover {
        border-color: #000;
        color: #000;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Engine
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
    # TOP HEADER SECTION (Logo, Text, Live Clock)
    # ---------------------------------------------------------
    head_col1, head_col2, head_col3 = st.columns([1, 4, 2])
    
    with head_col1:
        # Load logo from GitHub
        logo_url = "https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/logo.jpg"
        st.image(logo_url, width=80)
        
    with head_col2:
        st.markdown("<h1 style='margin-bottom: 0; padding-bottom: 0;'>Protthapan Technologies</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin-top: 0; padding-top: 0; color: #666;'>Inventory</h4>", unsafe_allow_html=True)
        
    with head_col3:
        # Custom HTML/JS for a LIVE ticking clock without page refresh
        clock_html = """
        <div style="background: white; padding: 10px; border-radius: 8px; border: 1px solid #ddd; text-align: center; font-family: sans-serif;">
            <div id="clock_date" style="font-size: 14px; color: #333;"></div>
            <div id="clock_time" style="font-size: 22px; font-weight: bold; color: #111; margin: 5px 0;"></div>
            <div id="clock_day" style="font-size: 14px; color: #666;"></div>
        </div>
        <script>
            function updateTime() {
                const now = new Date();
                const dOpts = { day: 'numeric', month: 'long', year: 'numeric' };
                document.getElementById('clock_date').innerText = now.toLocaleDateString('en-GB', dOpts);
                document.getElementById('clock_time').innerText = now.toLocaleTimeString('en-GB', { hour12: false });
                document.getElementById('clock_day').innerText = now.toLocaleDateString('en-GB', { weekday: 'long' });
            }
            setInterval(updateTime, 1000);
            updateTime();
        </script>
        """
        components.html(clock_html, height=100)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # SIDEBAR (Menu for Sort and Filter)
    # ---------------------------------------------------------
    st.sidebar.title("Controls")
    tab_sort, tab_filter = st.sidebar.tabs(["Sort", "Filter"])
    
    with tab_sort:
        sort_option = st.radio("Sort Inventory By:", [
            "Default (Serial No)", 
            "A to Z", 
            "Z to A", 
            "Price: High to Low", 
            "Price: Low to High"
        ])
        
    with tab_filter:
        cat_list = list(df['Category'].dropna().unique())
        selected_cats = st.multiselect("Select Categories:", cat_list, default=cat_list)
        
        max_cost = float(df['Cost'].max()) if not df.empty else 100000.0
        price_limit = st.slider("Max Price limit:", min_value=0.0, max_value=max_cost, value=max_cost)
        
        show_out_of_stock = st.checkbox("Only show Out of Stock items")

    # ---------------------------------------------------------
    # APPLY LOGIC (Filtering & Sorting)
    # ---------------------------------------------------------
    f_df = df.copy()
    
    # Apply Filters
    f_df = f_df[f_df['Category'].isin(selected_cats)]
    f_df = f_df[f_df['Cost'] <= price_limit]
    if show_out_of_stock:
        f_df = f_df[f_df['Physical Count'] <= 0]
        
    # Apply Sorting
    if sort_option == "A to Z":
        f_df = f_df.sort_values("Item Name", ascending=True)
    elif sort_option == "Z to A":
        f_df = f_df.sort_values("Item Name", ascending=False)
    elif sort_option == "Price: High to Low":
        f_df = f_df.sort_values("Cost", ascending=False)
    elif sort_option == "Price: Low to High":
        f_df = f_df.sort_values("Cost", ascending=True)

    # ---------------------------------------------------------
    # MODAL / POP-UP FUNCTION
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
            # Single line for Count, Unit, Cost
            st.write(f"**Count:** {item_data['Physical Count']} {item_data['Unit']} | **Cost:** INR {item_data['Cost']}")
            st.write("---")
            st.write(f"**Specifications:** {item_data['Specifications']}")
            st.write(f"**Description:** {item_data['Description']}")
            st.write(f"**Location:** {item_data['Location']}")

    # ---------------------------------------------------------
    # MAIN GRID DISPLAY (4 Items per line)
    # ---------------------------------------------------------
    # Create chunks of 4 for the grid
    rows = [f_df.iloc[i:i + 4] for i in range(0, len(f_df), 4)]

    for row in rows:
        cols = st.columns(4)
        for index, (df_index, item) in enumerate(row.iterrows()):
            with cols[index]:
                sku = str(item['SKU (ID)'])
                img_url = f"https://raw.githubusercontent.com/virajbhatt27/drone-inventory/main/assets/{sku}.jpg"
                
                # Render Image
                st.image(img_url, use_container_width=True)
                
                # Render Name and "i" Button side-by-side cleanly
                text_col, btn_col = st.columns([4, 1])
                with text_col:
                    st.write(f"**{item['Item Name']}**")
                with btn_col:
                    if st.button("i", key=f"info_{sku}"):
                        show_item_details(item)
else:
    st.error("Unable to load data. Please check the Google Sheet link.")
