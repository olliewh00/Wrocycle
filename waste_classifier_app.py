import streamlit as st
from PIL import Image
import os
from classifier_service import classify_waste

# Set page config for a clean minimalist UI
st.set_page_config(
    page_title="Wrocycle Helper",
    page_icon="♻️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Header layout with status indicator and minimalist styling
col_header, col_toggle = st.columns([3, 1])
with col_header:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin-top: 5px;">
        <span style="width: 8px; height: 8px; background-color: #10B981; border-radius: 50%; display: inline-block;"></span>
        <span style="font-size: 1.3rem; font-weight: 700; letter-spacing: -0.5px;">Wrocycle Helper</span>
    </div>
    <div style="font-size: 0.85rem; opacity: 0.5; margin-bottom: 20px;">Wrocław Dorm Waste Assistant • T-15 / T-17</div>
    """, unsafe_allow_html=True)
with col_toggle:
    is_dark = st.toggle("🌙 Dark Mode", value=True)

# Define clean minimalist colors based on selected theme
if is_dark:
    bg_color = "#09090B"      # zinc-950
    text_color = "#F4F4F5"    # zinc-100
    border_color = "#27272A"  # zinc-800
    card_bg = "#18181B"       # zinc-900
    shadow = "0 4px 20px rgba(0, 0, 0, 0.4)"
    tab_active = "#F4F4F5"
    tab_inactive = "#71717A"
    expander_bg = "#18181B"
    
    # Dark Mode specific color tints for result cards
    FRACTION_STYLES = {
        "YELLOW": {
            "bg": "#1E1A0A",
            "border": "#D97706",
            "text": "#F59E0B",
            "action_bg": "#D97706",
            "action_text": "#09090B",
            "name_pl": "METALE I TWORZYWA SZTUCZNE",
            "icon": "🟡"
        },
        "BLUE": {
            "bg": "#0D1B2A",
            "border": "#2563EB",
            "text": "#3B82F6",
            "action_bg": "#2563EB",
            "action_text": "#FFFFFF",
            "name_pl": "PAPIER",
            "icon": "🔵"
        },
        "GREEN": {
            "bg": "#062215",
            "border": "#059669",
            "text": "#10B981",
            "action_bg": "#059669",
            "action_text": "#FFFFFF",
            "name_pl": "SZKŁO",
            "icon": "🟢"
        },
        "BROWN": {
            "bg": "#231205",
            "border": "#92400E",
            "text": "#B45309",
            "action_bg": "#92400E",
            "action_text": "#FFFFFF",
            "name_pl": "BIO-ODPADY",
            "icon": "🟤"
        },
        "BLACK": {
            "bg": "#18181B",
            "border": "#52525B",
            "text": "#A1A1AA",
            "action_bg": "#52525B",
            "action_text": "#FFFFFF",
            "name_pl": "ODPADY ZMIESZANE",
            "icon": "⚫"
        },
        "STORE RETURN": {
            "bg": "#081E24",
            "border": "#0891B2",
            "text": "#06B6D4",
            "action_bg": "#0891B2",
            "action_text": "#09090B",
            "name_pl": "KAUCJA (DEPOSIT RETURN)",
            "icon": "♻️"
        },
        "RED": {
            "bg": "#270808",
            "border": "#DC2626",
            "text": "#EF4444",
            "action_bg": "#DC2626",
            "action_text": "#FFFFFF",
            "name_pl": "UBRANIA I BATERIE (SPECJALNE)",
            "icon": "🔴"
        }
    }
else:
    bg_color = "#FFFFFF"      # white
    text_color = "#18181B"    # zinc-900
    border_color = "#E4E4E7"  # zinc-200
    card_bg = "#FAFAFA"       # zinc-50
    shadow = "0 4px 15px rgba(0, 0, 0, 0.05)"
    tab_active = "#18181B"
    tab_inactive = "#A1A1AA"
    expander_bg = "#FFFFFF"
    
    # Light Mode specific color tints for result cards
    FRACTION_STYLES = {
        "YELLOW": {
            "bg": "#FEF3C7",
            "border": "#D97706",
            "text": "#92400E",
            "action_bg": "#D97706",
            "action_text": "#FFFFFF",
            "name_pl": "METALE I TWORZYWA SZTUCZNE",
            "icon": "🟡"
        },
        "BLUE": {
            "bg": "#EFF6FF",
            "border": "#2563EB",
            "text": "#1E40AF",
            "action_bg": "#2563EB",
            "action_text": "#FFFFFF",
            "name_pl": "PAPIER",
            "icon": "🔵"
        },
        "GREEN": {
            "bg": "#ECFDF5",
            "border": "#059669",
            "text": "#065F46",
            "action_bg": "#059669",
            "action_text": "#FFFFFF",
            "name_pl": "SZKŁO",
            "icon": "🟢"
        },
        "BROWN": {
            "bg": "#FEF3C7",
            "border": "#B45309",
            "text": "#78350F",
            "action_bg": "#B45309",
            "action_text": "#FFFFFF",
            "name_pl": "BIO-ODPADY",
            "icon": "🟤"
        },
        "BLACK": {
            "bg": "#F4F4F5",
            "border": "#71717A",
            "text": "#27272A",
            "action_bg": "#71717A",
            "action_text": "#FFFFFF",
            "name_pl": "ODPADY ZMIESZANE",
            "icon": "⚫"
        },
        "STORE RETURN": {
            "bg": "#ECFEFF",
            "border": "#0891B2",
            "text": "#0E7490",
            "action_bg": "#0891B2",
            "action_text": "#FFFFFF",
            "name_pl": "KAUCJA (DEPOSIT RETURN)",
            "icon": "♻️"
        },
        "RED": {
            "bg": "#FEF2F2",
            "border": "#DC2626",
            "text": "#991B1B",
            "action_bg": "#DC2626",
            "action_text": "#FFFFFF",
            "name_pl": "UBRANIA I BATERIE (SPECJALNE)",
            "icon": "🔴"
        }
    }

# Inject Minimalist CSS Stylesheet
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    .stApp {{
        font-family: 'Inter', sans-serif !important;
        background-color: {bg_color} !important;
        color: {text_color} !important;
        transition: background-color 0.2s ease, color 0.2s ease;
    }}
    
    /* Sleek card containers */
    .clean-card {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: {shadow};
        transition: all 0.2s ease-in-out;
    }}
    
    .clean-card:hover {{
        transform: translateY(-1px);
    }}
    
    /* Clean tab buttons */
    button[data-baseweb="tab"] {{
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        color: {tab_inactive} !important;
        border-bottom: 2px solid transparent !important;
        transition: all 0.2s ease !important;
        background-color: transparent !important;
        padding: 10px 16px !important;
    }}
    
    button[aria-selected="true"] {{
        color: {tab_active} !important;
        border-bottom: 2px solid {tab_active} !important;
    }}
    
    .streamlit-expanderHeader {{
        background-color: {expander_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        color: {text_color} !important;
        font-weight: 500 !important;
    }}
</style>
""", unsafe_allow_html=True)

# Top level navigation tabs on header
tab_sorter, tab_guide, tab_dorms = st.tabs(["🔍 Sorter", "📖 Waste Guide", "🏫 Dorm Instructions"])

# Tab 1: Sorter
with tab_sorter:
    subtab_camera, subtab_upload = st.tabs(["📸 Camera Snap", "📂 Upload Image"])
    image_input = None
    
    with subtab_camera:
        camera_img = st.camera_input("Place waste in front of camera:")
        if camera_img:
            image_input = camera_img
            
    with subtab_upload:
        uploaded_file = st.file_uploader("Select waste image file:", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image_input = uploaded_file
            
    if image_input is not None:
        try:
            pil_image = Image.open(image_input)
            
            with st.spinner("Analyzing..."):
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
            
            # Render Sleek Minimalist Output Box
            st.markdown(f"""
            <div class="clean-card" style="
                background-color: {style['bg']};
                border: 1px solid {style['border']};
                border-left: 8px solid {style['border']};
                margin-top: 15px;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-size: 0.75rem; font-weight: 700; letter-spacing: 0.8px; color: {style['text']}; text-transform: uppercase;">
                        {style['icon']} {style['name_pl']}
                    </span>
                    <span style="
                        font-size: 0.7rem;
                        font-weight: 800;
                        background-color: {style['border']};
                        color: #FFFFFF;
                        padding: 3px 10px;
                        border-radius: 4px;
                    ">
                        {bin_color} BIN
                    </span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 800; color: {style['text']}; letter-spacing: -0.5px; margin-bottom: 5px;">
                    {fraction}
                </div>
                <div style="font-size: 0.95rem; color: {style['text']}; opacity: 0.8; margin-bottom: 20px;">
                    Identified item: <b>{item}</b>
                </div>
                <hr style="border: 0; border-top: 1px solid {style['border']}; opacity: 0.2; margin: 15px 0;">
                <div style="
                    font-size: 1.25rem;
                    font-weight: 800;
                    color: {style['text']};
                ">
                    ⚡ ACTION: {action}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("🖼️ View captured frame"):
                st.image(pil_image, caption="Analyzed waste object", width="stretch")
                
        except Exception as e:
            st.error(f"❌ Error classifying the item: {str(e)}")
            st.info("💡 Ensure your API key is correctly loaded in the `.env` configuration file.")

# Tab 2: Guide
with tab_guide:
    st.write("Understand what each container category means and how items should be sorted.")
    
    # Iterate through all styles to output guide cards using the clean tints
    for key, style in FRACTION_STYLES.items():
        if key == "YELLOW":
            allowed = "Plastic bottles, aluminum/metal cans, snack wrappers, clean plastic cups/tubs, milk/juice cartons (Tetra Paks), metal lids."
            forbidden = "Medicine packaging, motor oil containers, electronic components, rubber."
        elif key == "BLUE":
            allowed = "Clean cardboard, notebooks, paper packaging, brochures, copy paper."
            forbidden = "Oily/dirty paper (pizza boxes with grease), paper towels, tissues, wet paper bags."
        elif key == "GREEN":
            allowed = "Glass bottles (beverage), glass jars for preserves and spreads (without metal lids)."
            forbidden = "Ceramics, porcelain, drinking glasses, mirrors, light bulbs, window glass."
        elif key == "BROWN":
            allowed = "Vegetable and fruit scraps, coffee grounds and paper tea bags, eggshells."
            forbidden = "Meat, animal bones, leftovers containing oil/fat, dairy products, cat/dog waste."
        elif key == "BLACK":
            allowed = "Greasy/soiled paper (e.g. oily pizza boxes), used tissues, grease-soaked wrappers, leftovers containing meat or bones, receipts, drinking glasses, ceramics."
            forbidden = "Electronics, batteries, hazardous waste, building materials, clothing."
        elif key == "STORE RETURN":
            allowed = "PET beverage bottles (up to 3L), aluminum cans (up to 1L), glass beer/soda bottles with deposit symbol."
            forbidden = "Do not place in standard bins. Take to store counters or reverse vending machines to claim refund cash."
        elif key == "RED":
            allowed = "Clothes, shoes, textile bags, alkaline or rechargeable batteries, chargers, small electronics (e-waste)."
            forbidden = "Must NEVER go into standard municipal trash containers. Use PCK clothing bins or drop boxes in supermarkets/dorms."
            
        st.markdown(f"""
        <div class="clean-card" style="
            background-color: {style['bg']};
            border: 1px solid {style['border']};
            border-left: 6px solid {style['border']};
        ">
            <h4 style="margin-top: 0; color: {style['text']}; font-weight: 700;">{style['icon']} {style['name_pl']}</h4>
            <div style="font-size: 0.85rem; color: {style['text']}; line-height: 1.5;">
                <p style="margin: 4px 0;"><b>Allowed:</b> {allowed}</p>
                <p style="margin: 4px 0;"><b>Note / Restrictions:</b> {forbidden}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Tab 3: Dorms
with tab_dorms:
    st.write("Quick reference tips to help PWr students avoid sorting mistakes in T-15, T-17, and T-19 dormitories.")
    
    st.markdown(f"""
    <div class="clean-card">
        <h5 style="margin-top: 0; font-weight: 700; color: #DC2626;">🚨 Top Rules to Prevent Fines</h5>
        <ul style="font-size: 0.85rem; padding-left: 20px; line-height: 1.5; margin-bottom: 0; opacity: 0.8;">
            <li><b>Oily Pizza Boxes:</b> Go to <b>Mixed Waste (Black Bin)</b>. Do not throw greasy cardboard in the Paper bin as it ruins the recycling process.</li>
            <li><b>Paper Coffee Cups:</b> Go to <b>Mixed Waste</b> because they are lined with liquid-proof plastic.</li>
            <li><b>Jar Lids:</b> Always unscrew metal lids and throw them in <b>Metals & Plastics (Yellow)</b> before placing the glass jar in <b>Glass (Green)</b>.</li>
            <li><b>Textiles & Batteries:</b> Put textiles in PCK clothing bins. Drop old batteries/chargers in lobby collection tubes. Never put them in regular trash.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="clean-card">
        <h5 style="margin-top: 0; font-weight: 700; color: #059669;">💡 Quick Tips</h5>
        <ul style="font-size: 0.85rem; padding-left: 20px; line-height: 1.5; margin-bottom: 0; opacity: 0.8;">
            <li><b>No washing needed:</b> Empty food remnants from packaging before throwing. Do not waste water washing them.</li>
            <li><b>Crush items:</b> Flatten plastic bottles and aluminum cans to save bin space in dorm waste corridors.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
