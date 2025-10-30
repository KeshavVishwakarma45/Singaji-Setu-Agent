import streamlit as st
from typing import Dict, Any


def apply_custom_styling():
    """Apply custom CSS styling for the application."""
    theme_base = st.get_option("theme.base")
    primary_color = "#2E7D32"
    hover_color = "#66BB6A"
    secondary_bg_color = "#FFFFFF" if theme_base == "light" else "#1E1E1E"

    st.markdown(
        f"""
    <style>
    .stApp {{ background-color: {"#f0f2f6" if theme_base == "light" else "#0F0F0F"}; }}
    
    /* Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, {primary_color} 0%, #43A047 100%);
        color: white;
        border-radius: 12px;
        padding: 12px 24px;
        border: none;
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.3);
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background: linear-gradient(135deg, #43A047 0%, {primary_color} 100%);
        box-shadow: 0 6px 20px rgba(46, 125, 50, 0.4);
        transform: translateY(-2px);
    }}
    
    /* Audio Recorder Container */
    .stAudio {{
        background: {secondary_bg_color};
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        border: 2px solid {primary_color};
    }}
    
    /* Audio Player */
    audio {{
        width: 100%;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{ gap: 16px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {secondary_bg_color};
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        padding: 12px 24px;
        transition: all 0.3s ease;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: {hover_color};
        color: white;
        transform: translateY(-2px);
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {primary_color} 0%, #43A047 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.3);
    }}
    
    /* Text Area */
    textarea:focus {{
        border-color: {primary_color} !important;
        box-shadow: 0 0 0 2px rgba(46, 125, 50, 0.2) !important;
    }}
    
    /* Info/Warning Boxes */
    .stAlert {{
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    
    /* Headers */
    h1, h2, h3 {{
        color: {primary_color};
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )


def display_extra_details(gemini_result: Dict[str, Any]):
    """Display extra details found in the Gemini result in an organized way."""
    if "extra_details" in gemini_result and gemini_result["extra_details"]:
        st.subheader("🔍 Extra Details Found:")
        extra_details = gemini_result["extra_details"]

        if isinstance(extra_details, dict):
            for key, value in extra_details.items():
                if value is not None and value != "":
                    st.markdown(f"**{key}:** {value}")
        elif isinstance(extra_details, list):
            for item in extra_details:
                if item:
                    st.markdown(f"• {item}")
        else:
            st.markdown(f"**Additional Information:** {extra_details}")


def get_default_schema() -> Dict[str, Any]:
    """
    Provides a default nested JSON schema for extracting details
    from a farmer's interview.
    """
    return {
        "farmerDetails": {
            "farmerName": "string (Full name of the farmer)",
            "village": "string (Village, Tehsil, and District if available)",
            "contactNumber": "string (10-digit mobile number, if provided)",
            "farmingExperienceYears": "number (Number of years in farming)",
            "householdSize": "number (Total number of family members)",
        },
        "farmDetails": {
            "totalLandSizeAcres": "number (Total acres of land owned or farmed)",
            "soilType": "string (e.g., 'Black', 'Red', 'Alluvial', 'Loam')",
            "primaryCrops": [
                "list of strings (Main crops grown, e.g., 'Wheat', 'Cotton')"
            ],
            "irrigationSource": "string (e.g., 'Canal', 'Well', 'Borewell', 'Rain-fed')",
        },
        "livestockDetails": {
            "hasLivestock": "boolean (Does the farmer own any farm animals?)",
            "animals": [
                {
                    "type": "string (e.g., 'Cow', 'Buffalo', 'Goat', 'Chicken')",
                    "count": "number (The number of animals of this type)",
                }
            ],
        },
        "challengesAndNeeds": {
            "mainChallenges": [
                "list of strings (Primary difficulties faced, e.g., 'Pest attacks', 'Low water', 'Market price')"
            ],
            "interestedInNewTech": "boolean (Is the farmer open to trying new technology or methods?)",
            "specificNeeds": [
                "list of strings (Specific help they are looking for, e.g., 'Loan information', 'Better seeds')"
            ],
        },
        "interviewMetadata": {
            "interviewerName": "string (Name of the person conducting the interview)",
            "interviewDate": "string (Date of the interview in YYYY-MM-DD format)",
            "summary": "string (A brief, 2-3 sentence summary of the entire conversation)",
        },
    }
