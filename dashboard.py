st.markdown("""
    <!-- USE HTML LINK TAGS INSTEAD OF @IMPORT FOR STREAMLIT -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <style>
    /* Force typography overrides across the entire app */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Target all our specific data/number elements with the mono font */
    .mono, .pick-stock, .pick-buy-badge, .pick-cell-val, .pick-cell-lbl, .sec-hdr-text, 
    .ticker-label, .ticker-val, .mood-value, .pick-rr, .pick-meta span, .sq-title, .sq-chip {
        font-family: 'JetBrains Mono', monospace !important;
    }

    html, body, .stApp { background:#07091A; color:#CBD5E1; }
    .block-container { padding: 0 0 4rem 0; max-width: 100%; }
    header[data-testid="stHeader"], #MainMenu, footer { display: none; }
    
    /* ... Keep the rest of your CSS below here ... */
    </style>
""", unsafe_allow_html=True)
