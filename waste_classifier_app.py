import streamlit as st
from PIL import Image
import os
from classifier_service import classify_waste

# Set page config for a premium, custom browser tab look
st.set_page_config(
    page_title="Wrocycle Helper - Wrocław Dorm Sorter",
    page_icon="♻️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom color scheme, icons, and glow variables for each fraction
FRACTION_STYLES = {
    "YELLOW": {
        "bg": "linear-gradient(135deg, #FFF9C4 0%, #FFE082 100%)",
        "text": "#1E293B",
        "border": "#FFB300",
        "glow": "255, 179, 0",
        "action_bg": "#DC2626",
        "action_text": "#FFFFFF",
        "name_pl": "METALE I TWORZYWA SZTUCZNE",
        "icon": "🟡"
    },
    "BLUE": {
        "bg": "linear-gradient(135deg, #E3F2FD 0%, #90CAF9 100%)",
        "text": "#0F172A",
        "border": "#1E88E5",
        "glow": "30, 136, 229",
        "action_bg": "#1565C0",
        "action_text": "#FFFFFF",
        "name_pl": "PAPIER",
        "icon": "🔵"
    },
    "GREEN": {
        "bg": "linear-gradient(135deg, #E8F5E9 0%, #A5D6A7 100%)",
        "text": "#0F172A",
        "border": "#4CAF50",
        "glow": "76, 175, 80",
        "action_bg": "#2E7D32",
        "action_text": "#FFFFFF",
        "name_pl": "SZKŁO",
        "icon": "🟢"
    },
    "BROWN": {
        "bg": "linear-gradient(135deg, #efebe9 0%, #bcaaa4 100%)",
        "text": "#2D1500",
        "border": "#8D6E63",
        "glow": "141, 110, 99",
        "action_bg": "#5D4037",
        "action_text": "#FFFFFF",
        "name_pl": "BIO-ODPADY",
        "icon": "🟤"
    },
    "BLACK": {
        "bg": "linear-gradient(135deg, #374151 0%, #111827 100%)",
        "text": "#F8FAFC",
        "border": "#4B5563",
        "glow": "75, 85, 99",
        "action_bg": "#DC2626",
        "action_text": "#FFFFFF",
        "name_pl": "ODPADY ZMIESZANE",
        "icon": "⚫"
    },
    "STORE RETURN": {
        "bg": "linear-gradient(135deg, #E0F7FA 0%, #80DEEA 100%)",
        "text": "#004D40",
        "border": "#00ACC1",
        "glow": "0, 172, 193",
        "action_bg": "#FF6F00",
        "action_text": "#FFFFFF",
        "name_pl": "KAUCJA (DEPOSIT RETURN)",
        "icon": "♻️"
    }
}

# Inject premium styled CSS (Outfit font, Radial gradient backdrops, Glassmorphic headers)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&family=Montserrat:wght@800;900&display=swap');
    
    /* Global Page Styling */
    .stApp {
        font-family: 'Outfit', sans-serif;
        background: radial-gradient(circle at top right, #1E1B4B 0%, #0F172A 70%, #020617 100%);
        background-attachment: fixed;
        color: #E2E8F0;
    }
    
    /* Wrocycle Header Card with Glassmorphism */
    .wrocycle-header {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 35px 25px;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 30px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.35);
        position: relative;
        overflow: hidden;
    }
    
    .wrocycle-title {
        font-size: 3.2rem;
        font-weight: 900;
        font-family: 'Montserrat', sans-serif;
        background: linear-gradient(135deg, #34D399 0%, #3B82F6 50%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
        letter-spacing: -1.5px;
    }
    
    .wrocycle-subtitle {
        font-size: 1.15rem;
        color: #94A3B8;
        margin-bottom: 20px;
        font-weight: 300;
        letter-spacing: 0.2px;
    }
    
    .wrocycle-badge {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(239, 68, 68, 0.15) 100%);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.1);
        text-transform: uppercase;
    }
    
    /* Interactive Tabs customization */
    .stTabs {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
    }
    
    /* Custom CSS to polish Streamlit native Tab selectors */
    button[data-baseweb="tab"] {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #64748B !important;
        transition: all 0.3s ease !important;
    }
    
    button[aria-selected="true"] {
        color: #10B981 !important;
    }
    
    /* Pulse glow animation for classification card */
    @keyframes glowPulse {
        0% { box-shadow: 0 0 15px rgba(var(--glow-color), 0.25); }
        50% { box-shadow: 0 0 35px rgba(var(--glow-color), 0.55); }
        100% { box-shadow: 0 0 15px rgba(var(--glow-color), 0.25); }
    }
    
    .decision-card-premium {
        animation: glowPulse 3.5s infinite ease-in-out;
        border-radius: 24px;
        padding: 35px;
        margin-top: 15px;
        margin-bottom: 30px;
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 2px solid var(--border-color);
    }
    
    .decision-card-premium:hover {
        transform: translateY(-5px);
    }
    
    /* Reference Cheat Sheet style */
    .ref-header-premium {
        font-size: 1.4rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-top: 40px;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .ref-grid-premium {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
        gap: 12px;
        margin-bottom: 30px;
    }
    
    .ref-card-premium {
        padding: 14px;
        border-radius: 12px;
        text-align: center;
        font-size: 0.8rem;
        font-weight: 600;
        line-height: 1.3;
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .ref-card-premium:hover {
        transform: scale(1.04);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    
    /* Custom styling for expanders */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Application Header - Wrocycle Helper
st.markdown("""
<div class="wrocycle-header">
    <h1 class="wrocycle-title">♻️ Wrocycle Helper</h1>
    <p class="wrocycle-subtitle">Split-Second Waste Sorting Assistant for Wrocław Dormitories</p>
    <div class="wrocycle-badge">⚡ Sprinting from T-15/T-17 to D-20 lecture</div>
</div>
""", unsafe_allow_html=True)

st.write("🏃 Grab a photo of your container or wrapper, and instantly see where it belongs in Wrocław's sorting system.")

# Input layout with modern visual tabs
tab_camera, tab_upload = st.tabs(["📷 Take a Live Photo", "📂 Upload Local Image"])
image_input = None

with tab_camera:
    camera_img = st.camera_input("Hold the item in front of your camera:")
    if camera_img:
        image_input = camera_img

with tab_upload:
    uploaded_file = st.file_uploader("Choose an image file from your system:", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image_input = uploaded_file

# Processing pipeline
if image_input is not None:
    try:
        # Load file into PIL image
        pil_image = Image.open(image_input)
        
        # Sleek animated spinner
        with st.spinner("🔮 Analyzing item with Vision AI..."):
            result = classify_waste(pil_image)
            
        # Extract variables from results
        bin_color = result.get("bin_color", "").upper().strip()
        fraction = result.get("fraction", "").upper().strip()
        item = result.get("item_identified", "Unknown Waste Item")
        action = result.get("action_required", "THROW AWAY").upper().strip()
        
        # Load style mappings
        style = FRACTION_STYLES.get(bin_color)
        if not style:
            # Smart fallbacks in case model changes formatting
            if "METAL" in fraction or "PLASTIC" in fraction:
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
            elif "MIX" in fraction:
                style = FRACTION_STYLES["BLACK"]
                bin_color = "BLACK"
            elif "KAUCJA" in fraction or "RETURN" in fraction:
                style = FRACTION_STYLES["STORE RETURN"]
                bin_color = "STORE RETURN"
            else:
                style = FRACTION_STYLES["BLACK"]
                bin_color = "BLACK"
        
        # Premium glowing color-coded output block
        st.markdown(f"""
        <div class="decision-card-premium" style="
            background: {style['bg']}; 
            color: {style['text']}; 
            --glow-color: {style['glow']}; 
            --border-color: {style['border']};
            box-shadow: 0 10px 25px rgba({style['glow']}, 0.25);
        ">
            <div style="font-size: 1.1rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2.5px; opacity: 0.75; text-align: center;">
                {style['icon']} {style['name_pl']} {style['icon']}
            </div>
            <div style="font-size: 3.4rem; font-weight: 900; text-align: center; margin: 12px 0 6px 0; text-transform: uppercase; line-height: 1.1; letter-spacing: -0.5px;">
                {fraction}
            </div>
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="
                    font-size: 1.3rem; 
                    font-weight: 800; 
                    background-color: rgba(0,0,0,0.1); 
                    padding: 6px 20px; 
                    border-radius: 30px; 
                    display: inline-block;
                ">
                    Throw in: <b>{bin_color} BIN</b>
                </div>
            </div>
            <div style="font-size: 1.1rem; font-weight: 600; text-align: center; margin-bottom: 20px; opacity: 0.85;">
                Detected: <b>{item}</b>
            </div>
            <hr style="border: 0; border-top: 1px solid rgba(0,0,0,0.1); margin: 15px 0;">
            <div style="text-align: center;">
                <div style="
                    font-size: 1.6rem; 
                    font-weight: 900; 
                    background-color: {style['action_bg']}; 
                    color: {style['action_text']}; 
                    padding: 12px 25px; 
                    border-radius: 12px; 
                    box-shadow: 0 8px 16px rgba(0,0,0,0.15); 
                    display: inline-block;
                    letter-spacing: 0.5px;
                ">
                    ⚡ ACTION: {action}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display image preview inside clean expander
        with st.expander("🖼️ View captured frame preview"):
            st.image(pil_image, caption="Analyzed waste object", width="stretch")
            
    except Exception as e:
        st.error(f"❌ Error classifying the item: {str(e)}")
        st.info("💡 Ensure your API key is correctly loaded in the `.env` configuration file.")

# Cheat Sheet Section with Hover Cards
st.markdown('<div class="ref-header-premium">Ekosystem Wrocław Quick Reference 🇵🇱</div>', unsafe_allow_html=True)

st.markdown("""
<div class="ref-grid-premium">
    <div class="ref-card-premium" style="background-color: #FFF9C4; color: #1E293B; border-color: #FFD54F;">
        🟡 PLASTICS & METALS<br><span style="font-size: 0.7rem; font-weight: 300;">Plastiki i Metale</span>
    </div>
    <div class="ref-card-premium" style="background-color: #E3F2FD; color: #0F172A; border-color: #90CAF9;">
        🔵 CLEAN PAPER<br><span style="font-size: 0.7rem; font-weight: 300;">Czysty Papier</span>
    </div>
    <div class="ref-card-premium" style="background-color: #E8F5E9; color: #0F172A; border-color: #A5D6A7;">
        🟢 GLASS BOTTLES<br><span style="font-size: 0.7rem; font-weight: 300;">Szkło Opakowaniowe</span>
    </div>
    <div class="ref-card-premium" style="background-color: #efebe9; color: #2D1500; border-color: #bcaaa4;">
        🟤 BIO-WASTE<br><span style="font-size: 0.7rem; font-weight: 300;">Bio-odpady</span>
    </div>
    <div class="ref-card-premium" style="background-color: #1F2937; color: #F9FAFB; border-color: #4B5563;">
        ⚫ MIXED WASTE<br><span style="font-size: 0.7rem; font-weight: 300;">Zgniłe / Zmieszane</span>
    </div>
    <div class="ref-card-premium" style="background-color: #E0F7FA; color: #004D40; border-color: #80DEEA;">
        ♻️ KAUCJA RETURN<br><span style="font-size: 0.7rem; font-weight: 300;">System Kaucji</span>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("📌 Wrocław Dorm Waste Rules & Fines Prevention"):
    st.markdown("""
    - **Oily Pizza Boxes**: 🍕 Always throw in **Mixed Waste (Black)**! If clean, the lid can be separated and thrown into **Paper (Blue)**.
    - **Tetra Paks**: 🧃 Milk and juice cartons are composite materials. Put them in **Plastics & Metals (Yellow)**, not Paper!
    - **Coffee Grounds**: ☕ Throw in **Bio-waste (Brown)**, but paper cups go to **Mixed Waste (Black)** because they are lined with plastic.
    - **Meat & Bones**: 🍗 Throw in **Mixed (Black)**, never in Bio!
    - **Deposit System (Kaucja)**: 💶 Look for the deposit logo on bottles/cans. Return them to any deposit return machine/store instead of throwing them away to get your cash back!
    """)
