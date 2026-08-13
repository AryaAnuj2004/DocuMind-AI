import streamlit as st

def apply_custom_styles():
    """
    Injects custom CSS for a clean, minimal light design system.
    Tabs have NO boxes or background fills—ONLY a clean underline bar under the active tab name.
    Chat messages feature crisp card styling.
    """
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Typography & Base Size */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 14.5px !important;
    }

    /* Hide Default Hamburger Menu & Footer, but Keep Sidebar Open Toggle Button Visible */
    #MainMenu { visibility: hidden !important; display: none !important; }
    footer { visibility: hidden !important; display: none !important; }
    
    /* Hide Heading Anchor Link Icons (hover links beside headings) without hiding regular markdown links */
    [data-testid="stHeaderActionElements"],
    a.header-action-link,
    a.anchor-link,
    a[aria-label*="Link to this heading"],
    a[aria-label*="Direct link"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
    }
    
    [data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
    }

    [data-testid="stCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        color: #0f172a !important;
        z-index: 999999 !important;
    }

    [data-testid="stSidebarCollapseButton"] {
        visibility: visible !important;
        color: #0f172a !important;
    }

    /* Shift Main Content & Sidebar Upwards */
    .block-container {
        padding-top: 3.8rem !important;
        padding-bottom: 2rem !important;
        max-width: 1320px !important;
        margin: 0 auto !important;
    }

    /* Tighten Divider Lines (hr) & Sidebar Element Spacing */
    hr {
        margin-top: 1.0rem !important;
        margin-bottom: 1.0rem !important;
        border-color: #e2e8f0 !important;
    }

    /* Keep App Header crisp and unfaded */
    .app-header {
        opacity: 1 !important;
        filter: none !important;
    }

    /* Plain and simple spinner styling (no box/borders) */
    [data-testid="stSpinner"] {
        margin-top: 8px !important;
        margin-bottom: 14px !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    [data-testid="stSpinner"] p,
    [data-testid="stSpinner"] span,
    [data-testid="stSpinner"] div {
        color: #475569 !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
    }

    /* Content Fade below spinner during active processing */
    .processing-content-fade {
        opacity: 0.4 !important;
        filter: grayscale(20%) !important;
        pointer-events: none !important;
        transition: opacity 0.3s ease !important;
    }

    /* Global Light Background */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
        color: #1e293b;
    }

    /* Streamlit Global Text Overrides - Darker Text & Prominent Headings */
    p, span, label, div {
        font-size: 0.94rem;
        color: #0f172a;
    }

    h1 { font-size: 2.2rem !important; font-weight: 750 !important; color: #0f172a !important; margin-top: 1.5rem !important; margin-bottom: 0.8rem !important; }
    h2 { font-size: 1.85rem !important; font-weight: 750 !important; color: #0f172a !important; margin-top: 1.5rem !important; margin-bottom: 0.8rem !important; }
    h3 { font-size: 1.62rem !important; font-weight: 750 !important; color: #0f172a !important; margin-top: 1.5rem !important; margin-bottom: 0.8rem !important; }
    h4 { font-size: 1.3rem !important; font-weight: 650 !important; color: #0f172a !important; margin-top: 1.2rem !important; margin-bottom: 0.6rem !important; }

    .stMarkdown, .stMarkdown p, .stMarkdown li {
        color: #0f172a !important;
        font-weight: 450 !important;
        line-height: 1.65 !important;
    }

    .stMarkdown strong, .stMarkdown b, strong, b {
        font-weight: 700 !important;
        color: #0f172a !important;
    }

    /* Sidebar Styling & Decent Compact Layout */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.02);
    }

    [data-testid="stSidebarHeader"] {
        padding-top: 0.5rem !important;
        padding-bottom: 0 !important;
    }

    [data-testid="stSidebarUserContent"] {
        display: flex;
        flex-direction: column;
        min-height: calc(100vh - 40px);
        padding: 0.1rem 1rem 1rem 1rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.6rem !important;
    }

    [data-testid="stSidebar"] hr {
        margin-top: 0.6rem !important;
        margin-bottom: 0.6rem !important;
        border-color: #e2e8f0 !important;
    }

    /* Sidebar Title & Typography Overrides */
    [data-testid="stSidebar"] h1 {
        font-size: 1.35rem !important;
        font-weight: 750 !important;
        color: #0f172a !important;
        margin-top: 0 !important;
        padding-top: 0 !important;
        margin-bottom: 0.2rem !important;
    }

    [data-testid="stSidebar"] h2 {
        font-size: 1.15rem !important;
        font-weight: 650 !important;
        color: #0f172a !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.3rem !important;
    }

    [data-testid="stSidebar"] h3 {
        font-size: 0.98rem !important;
        font-weight: 650 !important;
        color: #0f172a !important;
        margin-top: 0.4rem !important;
        margin-bottom: 0.2rem !important;
    }

    [data-testid="stSidebar"] label {
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        margin-bottom: 0.2rem !important;
    }

    /* Sidebar Footer Pinned to Bottom */
    .sidebar-footer-pinned {
        margin-top: auto !important;
        padding-top: 16px;
        border-top: 1px solid #e2e8f0;
        font-size: 0.78rem;
        color: #64748b;
        text-align: center;
        font-weight: 400;
        margin-bottom: 12px;
    }

    /* Header Container */
    .app-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    }

    .app-title {
        color: #ffffff !important;
        font-weight: 700;
        font-size: 1.65rem;
        letter-spacing: -0.3px;
        margin-bottom: 4px;
        line-height: 1.2;
    }

    .app-subtitle {
        color: #94a3b8 !important;
        margin: 6px 0 0 1px;
        font-size: 0.9rem;
        font-weight: 400;
        line-height: 1.4;
    }

    /* Light Cards & Containers */
    .glass-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: 0 1px 6px rgba(0, 0, 0, 0.02);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .glass-card h1, .glass-card h2, .glass-card h3, .glass-card h4 {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    .glass-card:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
    }

    /* Citation Badges */
    .citation-badge {
        display: inline-flex;
        align-items: center;
        background: #f1f5f9;
        color: #334155;
        border: 1px solid #cbd5e1;
        border-radius: 16px;
        padding: 4px 12px;
        font-size: 0.82rem;
        font-weight: 500;
        margin-top: 8px;
        margin-bottom: 8px;
    }

    /* Word Count Badge */
    .word-count-badge {
        display: inline-block;
        background: #059669;
        color: #ffffff;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 4px 14px;
        border-radius: 10px;
        box-shadow: 0 1px 4px rgba(5, 150, 105, 0.15);
    }

    /* Source Snippet Container */
    .snippet-container {
        background: #f8fafc;
        border-left: 3px solid #64748b;
        border-radius: 6px;
        padding: 12px 16px;
        margin-top: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #334155;
        line-height: 1.55;
        border-top: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
    }

    .snippet-title {
        color: #475569;
        font-weight: 600;
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }

    /* Evaluation Result Badges */
    .score-badge-correct {
        background: #d1fae5;
        color: #065f46;
        border: 1px solid #a7f3d0;
        padding: 5px 14px;
        border-radius: 6px;
        font-size: 0.84rem;
        font-weight: 600;
    }

    .score-badge-partial {
        background: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
        padding: 5px 14px;
        border-radius: 6px;
        font-size: 0.84rem;
        font-weight: 600;
    }

    /* MINIMAL TABS - NO BOX, ONLY UNDERLINE BAR UNDER ACTIVE TAB */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px !important;
        background-color: transparent !important;
        border-bottom: 1px solid #e2e8f0 !important;
        padding-bottom: 0px !important;
    }

    .stTabs [data-baseweb="tab"] {
        height: 38px !important;
        background: transparent !important;
        border: none !important;
        border-radius: 0px !important;
        color: #64748b !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        padding: 0px 4px !important;
        box-shadow: none !important;
        outline: none !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: transparent !important;
        color: #0f172a !important;
    }

    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: #0f172a !important;
        border: none !important;
        border-bottom: 2.5px solid #0f172a !important;
        font-weight: 600 !important;
        box-shadow: none !important;
    }

    /* Remove Streamlit default red highlight bar and default tab borders */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #0f172a !important;
        height: 2.5px !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        background-color: transparent !important;
    }

    /* Crisp Chat Message Styling */
    [data-testid="stChatMessage"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02) !important;
    }

    /* Buttons - Crisp White Text */
    .stButton>button {
        background: #0f172a !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 18px !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12) !important;
    }

    .stButton>button p,
    .stButton>button span,
    .stButton>button div {
        color: #ffffff !important;
    }

    .stButton>button:hover {
        background: #1e293b !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
    }

    .stButton>button:hover p,
    .stButton>button:hover span,
    .stButton>button:hover div {
        color: #ffffff !important;
    }

    /* Compact Sidebar Buttons & Download Buttons Styling */
    [data-testid="stSidebar"] .stButton>button,
    [data-testid="stSidebar"] .stDownloadButton>button {
        padding: 5px 14px !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        border-radius: 6px !important;
        min-height: auto !important;
        height: auto !important;
        line-height: 1.3 !important;
    }

    [data-testid="stSidebar"] .stDownloadButton>button {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    }

    [data-testid="stSidebar"] .stDownloadButton>button p,
    [data-testid="stSidebar"] .stDownloadButton>button span,
    [data-testid="stSidebar"] .stDownloadButton>button div {
        color: #0f172a !important;
        font-size: 0.78rem !important;
    }

    [data-testid="stSidebar"] .stDownloadButton>button:hover {
        background: #f1f5f9 !important;
        border-color: #94a3b8 !important;
    }

    /* Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.01);
    }

    .metric-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #0f172a;
    }

    .metric-label {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 3px;
    }
    
    /* Input Fields */
    .stTextInput input, .stTextArea textarea {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
        font-size: 0.88rem !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #64748b !important;
        box-shadow: 0 0 0 2px rgba(100, 116, 139, 0.15) !important;
    }

    /* Reduce File Uploader Caption Text Font Size */
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] [data-testid="stCaptionContainer"],
    [data-testid="stFileUploader"] [data-baseweb="typo-caption"],
    [data-testid="stFileUploader"] section + div {
        font-size: 0.5rem !important;
        color: #64748b !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
