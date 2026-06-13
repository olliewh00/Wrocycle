import streamlit as st
from PIL import Image
import os
from classifier_service import classify_waste

# Set page config for a clean minimalist UI
st.set_page_config(
    page_title="WroCycle Helper",
    page_icon="♻️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state for sorter mode
if "sorter_mode" not in st.session_state:
    st.session_state.sorter_mode = "camera"

# Inject premium CSS styles matching the Stitch mockups
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>

<style>
    /* Global overrides */
    .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #f8f9fa !important;
        color: #191c1d !important;
    }
    
    /* Hide default Streamlit top bar elements */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    .stDeployButton {
        display: none !important;
    }
    #MainMenu {
        visibility: hidden !important;
    }
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* Remove default streamlit container paddings */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        max-width: 800px !important;
    }
    
    /* Custom Header Bar */
    .custom-header {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid #e7e8e9;
        padding: 16px 24px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 0 0 24px 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
    }
    .custom-logo {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .custom-logo-text {
        font-size: 1.4rem;
        font-weight: 800;
        color: #004d27;
        letter-spacing: -0.5px;
    }
    .custom-meta {
        font-size: 0.8rem;
        color: #6f7a70;
        font-weight: 500;
    }
    
    /* Style Streamlit Tabs */
    div[data-testid="stTabBar"] {
        background-color: transparent !important;
        border-bottom: 1px solid #e1e3e4 !important;
        padding: 0 !important;
        margin-bottom: 28px !important;
        display: flex !important;
        justify-content: center !important;
    }
    
    div[data-testid="stTabBar"] > div {
        justify-content: center !important;
        gap: 8px !important;
    }
    
    button[data-baseweb="tab"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #3f4940 !important;
        padding: 14px 20px !important;
        transition: all 0.25s ease !important;
        border-bottom: 2px solid transparent !important;
        background-color: transparent !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    button[data-baseweb="tab"]:hover {
        color: #004d27 !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #004d27 !important;
        border-bottom: 2px solid #004d27 !important;
    }
    
    /* Style Streamlit Buttons */
    button[kind="secondary"] {
        background-color: #ffffff !important;
        border: 2px solid #bec9be !important;
        border-radius: 9999px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        color: #3f4940 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.85rem !important;
    }
    
    button[kind="secondary"]:hover {
        border-color: #004d27 !important;
        color: #004d27 !important;
        background-color: #f0fdf4 !important;
    }
    
    button[kind="primary"] {
        background-color: #004d27 !important;
        border: 2px solid #004d27 !important;
        border-radius: 9999px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(0, 77, 39, 0.15) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.85rem !important;
    }
    
    button[kind="primary"]:hover {
        background-color: #00331a !important;
        border-color: #00331a !important;
    }
    
    /* Style Expander headers */
    .streamlit-expanderHeader {
        background-color: #ffffff !important;
        border: 1px solid #e1e3e4 !important;
        border-radius: 16px !important;
        color: #191c1d !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        padding: 12px 18px !important;
        margin-top: 10px !important;
    }
    
    /* Viewfinder camera design */
    .viewfinder-wrapper {
        position: relative;
        border: 4px solid #e1e3e4;
        border-radius: 32px;
        padding: 12px;
        background: #ffffff;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        max-width: 450px;
        margin: 0 auto 24px auto;
        overflow: hidden;
    }
    .viewfinder-wrapper::before {
        content: '';
        position: absolute;
        top: 24px; left: 24px; right: 24px; bottom: 24px;
        border: 2px dashed rgba(0, 77, 39, 0.2);
        border-radius: 20px;
        pointer-events: none;
        z-index: 10;
    }
    .viewfinder-wrapper::after {
        content: '';
        position: absolute;
        left: 12px; right: 12px; height: 4px;
        background: rgba(0, 148, 68, 0.4);
        box-shadow: 0 0 12px rgba(0, 148, 68, 0.6);
        z-index: 15;
        animation: scan 3s infinite ease-in-out;
    }
    @keyframes scan {
        0%, 100% { top: 12px; }
        50% { top: calc(100% - 16px); }
    }
    
    /* Category grids styling */
    .pillar-card {
        background: #ffffff !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.02) !important;
        border-radius: 24px !important;
        padding: 24px !important;
        transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease !important;
        border: 1px solid rgba(0,0,0,0.03) !important;
    }
    .pillar-card:hover {
        transform: translateY(-6px) !important;
        box-shadow: 0 12px 28px rgba(0,0,0,0.06) !important;
    }
</style>
""", unsafe_allow_html=True)

# Render Custom Logo and Meta Header
st.markdown("""
<div class="custom-header">
    <div class="custom-logo">
        <span class="material-symbols-outlined text-primary text-3xl" style="color: #004d27; font-size: 32px;">recycling</span>
        <span class="custom-logo-text">WroCycle Helper</span>
    </div>
    <div class="custom-meta">
        Wrocław Dorm Waste Assistant
    </div>
</div>
""", unsafe_allow_html=True)

# Define clean mockup colors and symbols for waste fractions
FRACTION_STYLES = {
    "YELLOW": {
        "bg": "#FFFDE6",        # Soft light yellow
        "border": "#FFD200",    # Waste yellow
        "text": "#806900",      # Dark yellow text
        "name_pl": "METALE I TWORZYWA SZTUCZNE",
        "name_en": "METALS AND PLASTICS",
        "symbol": "recycling"
    },
    "BLUE": {
        "bg": "#E6F2FA",        # Soft light blue
        "border": "#0072BC",    # Waste blue
        "text": "#004775",      # Dark blue text
        "name_pl": "PAPIER",
        "name_en": "PAPER",
        "symbol": "description"
    },
    "GREEN": {
        "bg": "#E6F4EC",        # Soft light green
        "border": "#009444",    # Waste green
        "text": "#005C2B",      # Dark green text
        "name_pl": "SZKŁO",
        "name_en": "GLASS",
        "symbol": "wine_bar"
    },
    "BROWN": {
        "bg": "#F5ECE6",        # Soft light brown
        "border": "#8C6239",    # Waste brown
        "text": "#5C4125",      # Dark brown text
        "name_pl": "BIO-ODPADY",
        "name_en": "BIO-WASTE",
        "symbol": "compost"
    },
    "BLACK": {
        "bg": "#F2F2F2",        # Light grey
        "border": "#1A1A1A",    # Waste black
        "text": "#1A1A1A",      # Black text
        "name_pl": "ODPADY ZMIESZANE",
        "name_en": "MIXED WASTE",
        "symbol": "delete"
    },
    "STORE RETURN": {
        "bg": "#FFF5E6",        # Soft orange
        "border": "#DD6B20",    # Deposit orange
        "text": "#9C400B",      # Dark orange
        "name_pl": "KAUCJA (SYSTEM KAUCYJNY)",
        "name_en": "DEPOSIT RETURN",
        "symbol": "paid"
    },
    "RED": {
        "bg": "#FCECEC",        # Soft red
        "border": "#BA1A1A",    # Error red
        "text": "#7E1212",      # Dark red text
        "name_pl": "SPECJALNE (UBRANIA / ELEKTROŚMIECI)",
        "name_en": "SPECIAL (CLOTHES / E-WASTE)",
        "symbol": "warning"
    }
}

# Top navigation tabs matching Stitch menu options
tab_home, tab_game, tab_rules, tab_about = st.tabs([
    "🏠 Główna / Home",
    "🎮 Gra / Game",
    "📋 Zasady / Rules",
    "ℹ️ O projekcie / About"
])

# -----------------------------------------------------------------------------
# TAB 1: Główna / Home (Sorter & Scanner)
# -----------------------------------------------------------------------------
with tab_home:
    # Hero Header Block
    st.markdown("""
    <div style="text-align: center; padding: 12px 10px; font-family: 'Plus Jakarta Sans', sans-serif;">
        <div style="display: inline-flex; align-items: center; gap: 8px; color: #004d27; padding: 6px 16px; border-radius: 9999px; margin-bottom: 16px; font-size: 0.85rem; font-weight: 700; background: rgba(0, 77, 39, 0.08);">
            <span class="material-symbols-outlined" style="font-size: 16px; font-variation-settings: 'FILL' 1;">camera_enhance</span>
            Eko-Skaner AI / AI Eco-Scanner
        </div>
        <h1 style="font-size: 2.2rem; font-weight: 800; color: #191c1d; margin-bottom: 12px; line-height: 1.25; letter-spacing: -0.8px;">
            Nie wiesz gdzie wyrzucić? <span style="color: #009444;">Zeskanuj!</span><br>
            <span style="font-size: 1.5rem; font-weight: 600; opacity: 0.7;">Not sure where to throw? Scan it!</span>
        </h1>
        <p style="font-size: 1rem; color: #3f4940; max-width: 580px; margin: 0 auto 24px auto; line-height: 1.5;">
            Użyj aparatu, aby natychmiast rozpoznać rodzaj odpadu i przypisać go do właściwego kosza. / <span style="font-style: italic; opacity: 0.8; font-size: 0.9rem;">Use your camera to instantly recognize the waste type.</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mode selector buttons (Camera vs Upload)
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        btn_type = "primary" if st.session_state.sorter_mode == "camera" else "secondary"
        if st.button("📸 Uruchom Skaner / Launch Scanner", type=btn_type, use_container_width=True):
            st.session_state.sorter_mode = "camera"
            st.rerun()
    with col_btn2:
        btn_type = "primary" if st.session_state.sorter_mode == "upload" else "secondary"
        if st.button("📂 Prześlij Zdjęcie / Upload Photo", type=btn_type, use_container_width=True):
            st.session_state.sorter_mode = "upload"
            st.rerun()
            
    image_input = None
    
    # Render corresponding input widget
    if st.session_state.sorter_mode == "camera":
        st.markdown('<div class="viewfinder-wrapper">', unsafe_allow_html=True)
        camera_img = st.camera_input("Place waste in front of camera:", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        if camera_img:
            image_input = camera_img
    else:
        st.markdown('<div style="max-width: 450px; margin: 0 auto 24px auto;">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Select waste image file:", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        if uploaded_file:
            image_input = uploaded_file

    # Run AI waste classifier when image is input
    if image_input is not None:
        try:
            pil_image = Image.open(image_input)
            
            with st.spinner("Analizowanie... / Analyzing..."):
                result = classify_waste(pil_image)
                
            bin_color = result.get("bin_color", "").upper().strip()
            fraction = result.get("fraction", "").upper().strip()
            item = result.get("item_identified", "Unknown Item")
            action = result.get("action_required", "THROW AWAY").upper().strip()
            
            # Map styles with clean robust fallback
            style = FRACTION_STYLES.get(bin_color)
            if not style:
                if "RED" in bin_color or "BATTER" in fraction or "CLOTH" in fraction:
                    style = FRACTION_STYLES["RED"]
                    bin_color = "RED"
                elif "METAL" in fraction or "PLASTIC" in fraction:
                    style = FRACTION_STYLES["YELLOW"]
                    bin_color = "YELLOW"
                elif "PAPER" in fraction:
                    style = FRACTION_STYLES["BLUE"]
                    bin_color = "BLUE"
                elif "GLASS" in fraction:
                    style = FRACTION_STYLES["GREEN"]
                    bin_color = "GREEN"
                elif "BIO" in fraction:
                    style = FRACTION_STYLES["BROWN"]
                    bin_color = "BROWN"
                elif "KAUCJA" in fraction or "RETURN" in fraction:
                    style = FRACTION_STYLES["STORE RETURN"]
                    bin_color = "STORE RETURN"
                else:
                    style = FRACTION_STYLES["BLACK"]
                    bin_color = "BLACK"
            
            # Render Glowing Glassmorphic Result Card
            st.markdown(f"""
            <div style="
                background-color: {style['bg']};
                border: 2px solid {style['border']};
                border-left: 10px solid {style['border']};
                border-radius: 24px;
                padding: 24px;
                margin-top: 10px;
                margin-bottom: 24px;
                box-shadow: 0 12px 30px rgba(0,0,0,0.04);
                font-family: 'Plus Jakarta Sans', sans-serif;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 0.85rem; font-weight: 700; color: {style['text']}; text-transform: uppercase; letter-spacing: 0.8px; display: flex; align-items: center; gap: 8px;">
                        <span class="material-symbols-outlined" style="font-size: 22px;">{style['symbol']}</span>
                        {style['name_pl']} / <span style="font-weight: 500; opacity: 0.8;">{style['name_en']}</span>
                    </span>
                    <span style="
                        font-size: 0.7rem;
                        font-weight: 800;
                        background-color: {style['border']};
                        color: #ffffff;
                        padding: 4px 12px;
                        border-radius: 9999px;
                        text-transform: uppercase;
                    ">
                        {bin_color} BIN
                    </span>
                </div>
                <div style="font-size: 2rem; font-weight: 800; color: {style['text']}; letter-spacing: -0.5px; line-height: 1.15; margin-bottom: 8px;">
                    {fraction}
                </div>
                <div style="font-size: 1rem; color: #191c1d; margin-bottom: 16px;">
                    Identified item: <b style="color: {style['text']};">{item}</b>
                </div>
                <hr style="border: 0; border-top: 1px solid {style['border']}; opacity: 0.15; margin: 16px 0;">
                <div style="
                    font-size: 1.25rem;
                    font-weight: 800;
                    color: {style['text']};
                    display: flex;
                    align-items: center;
                    gap: 6px;
                ">
                    <span class="material-symbols-outlined">bolt</span>
                    AKCJA / ACTION: {action}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("🖼️ Zobacz kadr / View captured frame"):
                st.image(pil_image, caption="Analyzed waste object", use_container_width=True)
                
        except Exception as e:
            st.error(f"❌ Error classifying the item: {str(e)}")
            st.info("💡 Ensure your API key is correctly loaded in the `.env` configuration file.")

    # Five Pillars Section
    st.markdown("""
    <div style="margin-top: 48px; margin-bottom: 32px; font-family: 'Plus Jakarta Sans', sans-serif;">
        <h2 style="font-size: 1.6rem; font-weight: 700; color: #191c1d; margin-bottom: 6px; text-align: center; letter-spacing: -0.5px;">
            Pięć Filarów Segregacji / <span style="font-weight: 400; opacity: 0.7;">Five Pillars of Sorting</span>
        </h2>
        <p style="font-size: 0.95rem; color: #3f4940; text-align: center; margin-bottom: 28px;">
            Poznaj zasady sortowania odpadów we Wrocławiu. / <span style="font-style: italic;">Learn the waste sorting rules in Poland.</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 5 categories grid columns
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="pillar-card" style="border-top: 6px solid #FFD200; height: 190px;">
            <span class="material-symbols-outlined" style="font-size: 36px; color: #FFD200; margin-bottom: 12px; display: block;">recycling</span>
            <h3 style="font-size: 1.15rem; font-weight: 700; margin: 0 0 2px 0;">Metale i Tworzywa</h3>
            <p style="font-size: 0.8rem; color: #6f7a70; margin: 0 0 10px 0; font-weight: 500;">Metals and Plastics</p>
            <p style="font-size: 0.8rem; color: #3f4940; line-height: 1.4; margin: 0;">Puszki, butelki PET, kartony po sokach. / <span style="font-style: italic; opacity: 0.8;">Cans, PET bottles, cartons.</span></p>
        </div>
        <div style="height: 16px;"></div>
        <div class="pillar-card" style="border-top: 6px solid #009444; height: 190px;">
            <span class="material-symbols-outlined" style="font-size: 36px; color: #009444; margin-bottom: 12px; display: block;">wine_bar</span>
            <h3 style="font-size: 1.15rem; font-weight: 700; margin: 0 0 2px 0;">Szkło</h3>
            <p style="font-size: 0.8rem; color: #6f7a70; margin: 0 0 10px 0; font-weight: 500;">Glass</p>
            <p style="font-size: 0.8rem; color: #3f4940; line-height: 1.4; margin: 0;">Butelki i słoiki szklane. / <span style="font-style: italic; opacity: 0.8;">Jars and glass bottles.</span></p>
        </div>
        <div style="height: 16px;"></div>
        <div class="pillar-card" style="border-top: 6px solid #1A1A1A; height: 190px;">
            <span class="material-symbols-outlined" style="font-size: 36px; color: #1A1A1A; margin-bottom: 12px; display: block;">delete</span>
            <h3 style="font-size: 1.15rem; font-weight: 700; margin: 0 0 2px 0;">Zmieszane</h3>
            <p style="font-size: 0.8rem; color: #6f7a70; margin: 0 0 10px 0; font-weight: 500;">Mixed</p>
            <p style="font-size: 0.8rem; color: #3f4940; line-height: 1.4; margin: 0;">Hygiene items, greasy wrappers, meat remnants. / <span style="font-style: italic; opacity: 0.8;">Food residues.</span></p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="pillar-card" style="border-top: 6px solid #0072BC; height: 190px;">
            <span class="material-symbols-outlined" style="font-size: 36px; color: #0072BC; margin-bottom: 12px; display: block;">description</span>
            <h3 style="font-size: 1.15rem; font-weight: 700; margin: 0 0 2px 0;">Papier</h3>
            <p style="font-size: 0.8rem; color: #6f7a70; margin: 0 0 10px 0; font-weight: 500;">Paper</p>
            <p style="font-size: 0.8rem; color: #3f4940; line-height: 1.4; margin: 0;">Gazety, czyste kartony, zeszyty. / <span style="font-style: italic; opacity: 0.8;">Newspapers, dry cardboard.</span></p>
        </div>
        <div style="height: 16px;"></div>
        <div class="pillar-card" style="border-top: 6px solid #8C6239; height: 190px;">
            <span class="material-symbols-outlined" style="font-size: 36px; color: #8C6239; margin-bottom: 12px; display: block;">compost</span>
            <h3 style="font-size: 1.15rem; font-weight: 700; margin: 0 0 2px 0;">Bio</h3>
            <p style="font-size: 0.8rem; color: #6f7a70; margin: 0 0 10px 0; font-weight: 500;">Bio-waste</p>
            <p style="font-size: 0.8rem; color: #3f4940; line-height: 1.4; margin: 0;">Obierki owoców i warzyw, fusy po kawie. / <span style="font-style: italic; opacity: 0.8;">Vegetable residues.</span></p>
        </div>
        <div style="height: 16px;"></div>
        <div class="pillar-card" style="border-top: 6px solid #dd6b20; height: 190px;">
            <span class="material-symbols-outlined" style="font-size: 36px; color: #dd6b20; margin-bottom: 12px; display: block;">paid</span>
            <h3 style="font-size: 1.15rem; font-weight: 700; margin: 0 0 2px 0;">System Kaucyjny</h3>
            <p style="font-size: 0.8rem; color: #6f7a70; margin: 0 0 10px 0; font-weight: 500;">Deposit Return</p>
            <p style="font-size: 0.8rem; color: #3f4940; line-height: 1.4; margin: 0;">Zwrotne butelki szklane, plastikowe i puszki. / <span style="font-style: italic; opacity: 0.8;">Return for cash refund.</span></p>
        </div>
        """, unsafe_allow_html=True)

    # CTA Section to Game
    st.markdown("""
    <div style="background-color: #006837; border-radius: 28px; padding: 32px; color: #ffffff; display: flex; flex-direction: column; justify-content: space-between; gap: 20px; margin-top: 40px; margin-bottom: 32px; font-family: 'Plus Jakarta Sans', sans-serif; box-shadow: 0 10px 25px rgba(0, 104, 55, 0.15);">
        <div>
            <h2 style="font-size: 1.8rem; font-weight: 800; color: #ffffff; margin: 0 0 8px 0; letter-spacing: -0.5px;">Graj i Ucz się! / <span style="font-weight: 400; opacity: 0.85;">Play & Learn!</span></h2>
            <p style="font-size: 0.95rem; opacity: 0.9; line-height: 1.5; margin: 0;">
                Sprawdź swoją wiedzę w naszej grze edukacyjnej. Zgarniaj punkty sortując odpady ruchem przesunięcia karty! / <span style="font-style: italic; opacity: 0.8;">Test your sorting skills in our interactive Tinder-style swipe game.</span>
            </p>
        </div>
        <div style="display: flex; align-items: center; justify-content: flex-start; gap: 8px;">
            <span class="material-symbols-outlined" style="font-size: 20px;">sports_esports</span>
            <span style="font-weight: 700; font-size: 0.9rem;">Przejdź do zakładki GRA na górze, aby zacząć! / Switch to the GAME tab above to start!</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Newsletter signup
    st.markdown("""
    <div style="background: #ffffff; border: 1px solid #e1e3e4; border-radius: 24px; padding: 32px; text-align: center; font-family: 'Plus Jakarta Sans', sans-serif; margin-bottom: 24px; box-shadow: 0 8px 20px rgba(0,0,0,0.01);">
        <h3 style="font-size: 1.4rem; font-weight: 700; margin: 0 0 6px 0;">Chcesz wiedzieć więcej? / <span style="font-weight: 400; opacity: 0.7;">Want to know more?</span></h3>
        <p style="font-size: 0.9rem; color: #6f7a70; margin: 0 0 20px 0;">Zapisz się do naszego eko-poradnika na PWr. / <span style="font-style: italic;">Subscribe to receive waste management guidelines and dormitory updates.</span></p>
        <div style="display: flex; gap: 10px; max-width: 450px; margin: 0 auto;">
            <input type="email" placeholder="Twój e-mail / Email address" style="flex-grow: 1; border: 2px solid #bec9be; border-radius: 9999px; padding: 12px 20px; font-family: inherit; font-size: 0.85rem; outline: none;" />
            <button style="background: #004d27; color: #ffffff; border: none; border-radius: 9999px; padding: 0 24px; font-weight: 700; font-family: inherit; font-size: 0.85rem; cursor: pointer; white-space: nowrap;">Zapisz / Join</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 2: Gra / Game (Embedded Tinder-style swiper)
# -----------------------------------------------------------------------------
with tab_game:
    # Read wrocycle_game.html with css header/footer stripper
    filepath = os.path.join(os.path.dirname(__file__), "stitch_screens", "wrocycle_game.html")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Inject style override to hide mockup page wrapper header/footer
        hide_style = """
        <style>
            header { display: none !important; }
            footer { display: none !important; }
            body { 
                padding: 0 !important; 
                margin: 0 !important;
                background: transparent !important; 
            }
            main {
                padding-top: 0 !important;
                padding-bottom: 0 !important;
            }
        </style>
        """
        html_content = html_content.replace("</head>", f"{hide_style}</head>")
        
        # Embed the HTML/JS Component
        st.components.v1.html(html_content, height=800, scrolling=True)
    else:
        st.error("❌ Gra nie mogła zostać załadowana. Brak pliku wrocycle_game.html / Game file not found.")

# -----------------------------------------------------------------------------
# TAB 3: Zasady / Rules (Waste Guide)
# -----------------------------------------------------------------------------
with tab_rules:
    st.markdown("""
    <div style="padding: 10px 0; font-family: 'Plus Jakarta Sans', sans-serif;">
        <h2 style="font-size: 1.6rem; font-weight: 700; margin-bottom: 8px;">Szczegółowy Przewodnik / <span style="font-weight: 400; opacity: 0.7;">Detailed Waste Guide</span></h2>
        <p style="color: #6f7a70; font-size: 0.95rem; margin-bottom: 24px;">Zapoznaj się z dokładnymi regułami segregacji we Wrocławiu. / <span style="font-style: italic;">Follow the exact municipal rules.</span></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Iterate guide categories
    for key, style in FRACTION_STYLES.items():
        if key == "YELLOW":
            allowed = "Plastic bottles, aluminum/metal cans, snack wrappers, clean plastic cups/tubs, milk/juice cartons (Tetra Paks), metal lids, tubes."
            forbidden = "Medicine packaging, motor oil containers, electronic components, rubber, toys, dirty packaging."
        elif key == "BLUE":
            allowed = "Clean cardboard, notebooks, paper packaging, brochures, copy paper, paper bags."
            forbidden = "Oily/dirty paper (pizza boxes with grease), paper towels, tissues, wet paper bags, grease-stained bags."
        elif key == "GREEN":
            allowed = "Glass bottles (beverage), glass jars for preserves and spreads (without metal lids)."
            forbidden = "Ceramics, porcelain, drinking glasses, mirrors, light bulbs, window glass, heat-resistant dishes."
        elif key == "BROWN":
            allowed = "Vegetable and fruit scraps, coffee grounds and paper tea bags, eggshells, clean food scraps."
            forbidden = "Meat, animal bones, leftovers containing oil/fat, dairy products, cat/dog waste, soil."
        elif key == "BLACK":
            allowed = "Greasy/soiled paper (e.g. oily pizza boxes), used tissues, grease-soaked wrappers, leftovers containing meat or bones, receipts, drinking glasses, ceramics, diapers."
            forbidden = "Electronics, batteries, hazardous waste, building materials, clothing, medicines."
        elif key == "STORE RETURN":
            allowed = "PET beverage bottles (up to 3L), aluminum cans (up to 1L), glass beer/soda bottles with deposit symbol."
            forbidden = "Do not place in standard bins. Take to store counters or reverse vending machines to claim refund cash."
        elif key == "RED":
            allowed = "Clothes, shoes, textile bags, alkaline or rechargeable batteries, chargers, small electronics (e-waste), bulbs."
            forbidden = "Must NEVER go into standard municipal trash containers. Use collection tubes or special drop boxes."

        st.markdown(f"""
        <div class="pillar-card" style="border-left: 8px solid {style['border']}; margin-bottom: 20px; padding: 20px;">
            <h3 style="color: {style['text']}; display: flex; align-items: center; gap: 8px; font-weight: 700; margin: 0 0 12px 0; font-size: 1.2rem;">
                <span class="material-symbols-outlined" style="font-size: 24px;">{style['symbol']}</span>
                {style['name_pl']} / <span style="font-weight: 500; opacity: 0.85;">{style['name_en']}</span>
            </h3>
            <div style="font-size: 0.88rem; color: #191c1d; line-height: 1.5;">
                <p style="margin: 4px 0;"><b>🟢 Wrzucamy / Allowed:</b> {allowed}</p>
                <p style="margin: 4px 0; color: #7e1212;"><b>🔴 Unikamy / Forbidden:</b> {forbidden}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 4: O projekcie / About (Dorm Instructions)
# -----------------------------------------------------------------------------
with tab_about:
    st.markdown("""
    <div style="padding: 10px 0; font-family: 'Plus Jakarta Sans', sans-serif;">
        <h2 style="font-size: 1.6rem; font-weight: 700; margin-bottom: 8px;">Poradnik Akademika / <span style="font-weight: 400; opacity: 0.7;">Dormitory Sorting Rules</span></h2>
        <p style="color: #6f7a70; font-size: 0.95rem; margin-bottom: 24px;">Jak uniknąć kar i sprawnie segregować w akademikach PWr (T-15, T-17, T-19). / <span style="font-style: italic;">Prevent dormitory fines.</span></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="pillar-card" style="border-left: 8px solid #ba1a1a; margin-bottom: 20px; padding: 20px;">
        <h3 style="color: #7e1212; display: flex; align-items: center; gap: 8px; font-weight: 700; margin: 0 0 12px 0; font-size: 1.2rem;">
            <span class="material-symbols-outlined">gavel</span>
            🚨 Kluczowe Reguły / Top Rules to Prevent Fines
        </h3>
        <ul style="font-size: 0.9rem; line-height: 1.6; margin: 0; padding-left: 20px; color: #3f4940;">
            <li><b>Brudny karton po pizzy:</b> Wrzucaj do <b>odpadów zmieszanych (czarny kosz)</b>. Tłuszcz uniemożliwia recykling makulatury.</li>
            <li><b>Papierowe kubki po kawie:</b> Trafiają do <b>zmieszanych</b> z uwagi na wewnętrzną laminację plastikiem.</li>
            <li><b>Nakrętki słoików:</b> Zawsze odkręcaj i wrzucaj do <b>tworzyw/metali (żółty kosz)</b>, a sam słoik do <b>szkła (zielony)</b>.</li>
            <li><b>Baterie i elektrośmieci:</b> Korzystaj ze specjalnych tub w holu lub oddawaj w supermarketach. Nigdy nie wyrzucaj do ogólnych koszy.</li>
        </ul>
    </div>
    
    <div class="pillar-card" style="border-left: 8px solid #009444; margin-bottom: 20px; padding: 20px;">
        <h3 style="color: #005c2b; display: flex; align-items: center; gap: 8px; font-weight: 700; margin: 0 0 12px 0; font-size: 1.2rem;">
            <span class="material-symbols-outlined">lightbulb</span>
            💡 Szybkie Wskazówki / Quick Tips
        </h3>
        <ul style="font-size: 0.9rem; line-height: 1.6; margin: 0; padding-left: 20px; color: #3f4940;">
            <li><b>Nie myj opakowań:</b> Wystarczy opróżnić resztki jedzenia. Szkoda czystej wody na mycie śmieci.</li>
            <li><b>Zgniataj odpady:</b> Zawsze zgniataj butelki PET i puszki przed wyrzuceniem, aby oszczędzać cenne miejsce w zsypie.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Render Custom Footer
st.markdown("""
<hr style="border: 0; border-top: 1px solid #e1e3e4; margin-top: 48px; margin-bottom: 24px;">
<div style="text-align: center; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.8rem; color: #6f7a70; padding-bottom: 24px;">
    <div style="display: flex; justify-content: center; align-items: center; gap: 6px; margin-bottom: 8px; color: #004d27; font-weight: 700;">
        <span class="material-symbols-outlined" style="font-size: 18px;">eco</span>
        EkoSzkoła / WroCycle Polska
    </div>
    © 2026 EkoSzkoła Polska. Razem dla czystej planety. / <span style="font-style: italic;">Together for a clean planet.</span><br>
    Zasady zgodne z wytycznymi Ekosystem Wrocław 2026.
</div>
""", unsafe_allow_html=True)
